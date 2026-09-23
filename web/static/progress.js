(() => {
  const form = document.querySelector('form[data-download-form]');
  if (!form) return;
  const panel = document.querySelector('#progress-panel');
  const log = document.querySelector('#progress-log');
  const status = document.querySelector('#progress-status');
  let running = false;
  form.addEventListener('submit', async (event) => {
    if (event.submitter?.value === 'list') return;
    event.preventDefault();
    if (running) return;
    running = true;
    const data = new FormData(form);
    if (event.submitter?.name) data.set(event.submitter.name, event.submitter.value);
    const buttons = [...form.querySelectorAll('button')];
    buttons.forEach(button => button.disabled = true);
    document.querySelector('#download-results')?.remove();
    document.querySelector('#request-error')?.remove();
    form.after(panel);
    panel.hidden = false;
    log.textContent = '';
    status.textContent = 'Descarga en curso…';
    const id = [...crypto.getRandomValues(new Uint8Array(16))].map(v => v.toString(16).padStart(2, '0')).join('');
    let stop = false;
    let resultHTML = '';
    let offset = 0;
    let pendingPoll = null;
    async function readProgress() {
      try {
        const response = await fetch(`/progress/${id}?offset=${offset}`, {cache: 'no-store'});
        if (response.ok) {
          const progress = await response.json();
          const atBottom = log.scrollTop + log.clientHeight >= log.scrollHeight - 30;
          offset = progress.offset;
          log.append(document.createTextNode(progress.log.replace(/\x1b\[[0-9;]*[A-Za-z]/g, '').replace(/\r/g, '\n')));
          if (progress.more) return true;
          if (atBottom) log.scrollTop = log.scrollHeight;
          resultHTML = progress.results || resultHTML;
        }
      } catch (_) { /* Download response remains the source of completion/errors. */ }
    }
    function poll() {
      if (!pendingPoll) pendingPoll = (async () => {
        while (await readProgress()) { /* Drain output in ordered chunks. */ }
      })().finally(() => { pendingPoll = null; });
      return pendingPoll;
    }
    const polling = (async () => {
      while (!stop) {
        await poll();
        if (!stop) await new Promise(resolve => setTimeout(resolve, 600));
      }
    })();
    try {
      const response = await fetch(form.getAttribute('action') || location.href, {
        method: 'POST', body: data, headers: {'X-Progress-ID': id}
      });
      if (response.ok && response.headers.get('Content-Type')?.includes('application/zip')) {
        const blob = await response.blob();
        await poll();
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.href = url; link.download = 'podcasts.zip'; link.textContent = 'Guardar ZIP';
        panel.append(link); link.click();
        setTimeout(() => { URL.revokeObjectURL(url); link.remove(); }, 60000);
        if (resultHTML) panel.insertAdjacentHTML('afterend', resultHTML);
      } else {
        const html = new DOMParser().parseFromString(await response.text(), 'text/html');
        const result = html.querySelector('#download-results');
        const error = html.querySelector('[role="alert"]');
        if (result) panel.after(result);
        if (error) { error.id = 'request-error'; panel.after(error); }
        if (!response.ok && !error) throw new Error(`El servidor devolvió un error (${response.status}).`);
      }
      status.textContent = response.ok ? 'Proceso terminado. Revisa los resultados.' : 'No se pudo completar el proceso.';
    } catch (error) {
      status.textContent = `No se pudo recibir el resultado: ${error.message}. El servidor puede seguir descargando; evita reenviar el lote.`;
    } finally {
      stop = true;
      await polling;
      await poll();
      running = false;
      buttons.forEach(button => button.disabled = false);
    }
  });
})();
