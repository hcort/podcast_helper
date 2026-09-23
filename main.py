"""
    Main entry point

    In main method we can build a list of podcast episodes to download,
    and they will be processed one by one
"""
from services.podcasts import PodcastService
from utils import read_config_object


if __name__ == '__main__':
    output_path_def = read_config_object()['output_folder']
    podcasts = PodcastService(output_path_def)
    url = None
    # url = 'https://podcasts.apple.com/us/podcast/the-gene-wolfe-literary-podcast/id1305307750'
    # url = 'https://podcasts.apple.com/us/podcast/alzabo-soup/id1150623452'
    # url = 'https://alzabosoup.libsyn.com/rss'
    # url = 'https://podcasts.apple.com/us/podcast/the-middle-earth-mixer/id1627995604'
    # url = 'https://www.ivoox.com/podcast-gamerah-noche_sq_f11463506_1.html'
    # url = 'https://www.ivoox.com/podcast-indiario_sq_f12394833_1.html'
    # url = 'https://www.ivoox.com/podcast-cuantica-grafica-podcast_sq_f11821502_1.html'
    # url = 'https://www.ivoox.com/podcast-viruete-com-el-podcast_sq_f1150250_1.html'
    # url = 'https://www.ivoox.com/podcast-checkpoint_sq_f1759733_1.html'
    # url = 'https://www.ivoox.com/podcast-casa-cavestany_sq_f11213468_1.html'
    # url = 'https://www.ivoox.com/podcast-menudas-vinetas_sq_f12313586_1.html'
    # url = 'https://www.ivoox.com/podcast-foxverso_sq_f11193172_1.html'
    # url = 'https://www.ivoox.com/podcast-vuelo-180-podcast_sq_f146234_1.html'
    # url = 'https://www.youtube.com/watch?v=aEqFxpRAjNI&list=UULF8RfCCzWsMgNspTI-GTFenQ'
    # url = 'https://www.ivoox.com/podcast-enano-blanco-30_sq_f11879935_1.html'
    # url = 'https://www.ivoox.com/podcast-tom-morello8217s-maximum-firepower_sq_f11198474_1.html'
    # url = 'https://www.ivoox.com/podcast-cantabria-oculta_sq_f1247441_1.html'
    # url = 'https://www.ivoox.com/podcast-hora-chinaski_sq_f11341595_1.html'
    if url:
        episode_list = podcasts.list_episodes(url)
    else:
        episode_list = [
            # 'https://www.youtube.com/watch?v=NZyXxDH6c8k',
        #     # 'https://www.ivoox.com/systema-maestro-25-los-pitufos-audios-mp3_rf_124926066_1.html'
        #     # 'https://www.youtube.com/watch?v=S__vx16_T9k',
        #     # 'https://www.ivoox.com/mv-11-comics-no-ficcion-para-peques-audios-mp3_rf_127180939_1.html',
        #     # 'https://www.ivoox.com/mv-04-comics-para-primeros-lectores-audios-mp3_rf_120896772_1.html',
        #     # 'https://www.ivoox.com/mv-09-dragones-dragonas-del-comic-infantil-audios-mp3_rf_124514554_1.html'
        #     'https://www.ivoox.com/programa-206-omc-315-peligrosas-sociales-audios-mp3_rf_81567895_1.html',
        #     'https://www.ivoox.com/cuantica-grafica-podcast-04-8211-acuerdos-secuestros-audios-mp3_rf_108666637_1.html',
        #     'https://www.ivoox.com/82-canciones-quemadas-canciones-cansinas-audios-mp3_rf_112292651_1.html',
        #     'https://www.ivoox.com/89-viva-jugar-juegos-con-astrochechu-audios-mp3_rf_123155341_1.html',
        #     'https://www.ivoox.com/81-treat-williams-megadrive-deep-rising-audios-mp3_rf_110467964_1.html',
        #     'https://www.ivoox.com/ck-271-elige-tu-propia-aventura-librojuegos-audios-mp3_rf_114170555_1.html',
        #     'https://www.ivoox.com/vuelo-180-6h-elige-tu-propia-desdicha-audios-mp3_rf_4723632_1.html',
        #     'https://www.ivoox.com/eligetupropiaaventura-capitulo-96-elige-tu-propio-audios-mp3_rf_127868233_1.html',
        #     'https://www.ivoox.com/13a-a-bailar-caribe-mix-audios-mp3_rf_41796672_1.html',
        #     'https://podcasts.apple.com/gb/podcast/nuestra-guerra/id1739571598?i=1000660487380',
        #     'https://www.youtube.com/watch?v=lhckja1LTts'
        #     'https://www.ivoox.com/hab-920-eduardo-torres-dulce-las-vidas-has-audios-mp3_rf_131520752_1.html',
        #     'https://www.ivoox.com/hab-919-andres-trapiello-lo-extravagante-es-la-audios-mp3_rf_131239206_1.html',
        #     'https://www.ivoox.com/hab-916-alcala-norte-la-vida-canon-audios-mp3_rf_130291060_1.html',
        #     'https://www.ivoox.com/hab-821-luis-alberto-cuenca-al-final-audios-mp3_rf_123958747_1.html',
        #     'https://www.ivoox.com/gamerah-noche-a3-24-el-dlcen-ring-audios-mp3_rf_131766947_1.html',
        #      'https://www.ivoox.com/ms-dos-club-8211-vol-48-heroes-of-audios-mp3_rf_133252181_1.html',
        #     'https://www.youtube.com/watch?v=CQNndYLFejU',
        #     'https://youtube.com/watch?v=aEqFxpRAjNI',
        #     'https://www.youtube.com/watch?v=40xuZeUhJRQ',
        #     'https://www.youtube.com/watch?v=YYl8GOv5YGk',
        #     'https://www.youtube.com/watch?v=7w6l0-MrZ5Y',
        #     'https://www.youtube.com/watch?v=m_YMB0sMKT4',
        #     'https://m.youtube.com/watch?v=KX-0Xw6kkrc',
        #     'https://www.youtube.com/watch?v=tSwGsJPHoww',
        #     'https://www.youtube.com/watch?v=3pfsSh_fTAc',
        #     'https://www.youtube.com/watch?v=cJgynRuMxpc',
        #     'https://www.youtube.com/watch?v=RTWwI-7qyLE',
        #     'https://www.youtube.com/watch?v=Rnalr9VuwJs',
        #     'https://www.youtube.com/watch?v=ZpifAd-3_58',
        #     'https://www.youtube.com/watch?v=BePTuan-5A8',
        #     'https://www.youtube.com/watch?v=T07FOdnqp_U',
        #     'https://www.ivoox.com/mv-17-parque-infantil-jurasico-audios-mp3_rf_134329643_1.html',
        #     'https://www.youtube.com/watch?v=gKAVL0L6pEo',
        #     'https://www.youtube.com/watch?v=x16QuOfmGqQ',
        #     'https://www.ivoox.com/fase-bonus-192-de-conan-a-gladiator-audios-mp3_rf_18631649_1.html',
        #     'https://www.youtube.com/watch?v=DFYc1EHV8JA',
        #     'https://www.youtube.com/watch?v=iHHXTanxTXg',
        #     'https://www.youtube.com/watch?v=SPCFWn_Upes',
        #     'https://www.youtube.com/watch?v=9rPrYvky0nY',
        #     'https://www.youtube.com/watch?v=A9gHO8-CKyU',
        #     'https://www.youtube.com/watch?v=2awFXcIlj2g',
        #     'https://www.youtube.com/watch?v=2bVypITXiOI',  # jesús maestro en dos idiomas
        #     'https://www.youtube.com/watch?v=KxyCDmKEzs8',  # jesús maestro en dos idiomas
        #     'https://www.youtube.com/watch?v=SjDhWE0HEMw',
        #     'https://www.youtube.com/watch?v=iVf7TNPlWzE',
        #     'https://www.youtube.com/watch?v=iGLzWdT7vGc',
        #     'https://www.youtube.com/watch?v=GopJ1x7vK2Q',
        #     'https://www.ivoox.com/episodio-23-marzo-1994-audios-mp3_rf_125898365_1.html',
        #     'https://www.ivoox.com/floppy-87-8211-la-industria-del-videojuego-espanol-audios-mp3_rf_137906812_1.html',
        #     'https://www.ivoox.com/floppy-82-8211-la-aventura-grafica-legends-of-audios-mp3_rf_135548902_1.html',
        #     'https://www.ivoox.com/ck-118-culturismo-pop-audios-mp3_rf_21469027_1.html',
        #     'https://www.ivoox.com/episodio-33-enero-1995-audios-mp3_rf_138197024_1.html',
        #     'https://www.ivoox.com/ck-307-recordando-el-pequeno-pais-goomer-leo-verdura-audios-mp3_rf_137579801_1.html',
        #     'https://www.ivoox.com/minigeotrichum-la-falsa-muerte-aventuras-audios-mp3_rf_124717954_1.html',
        #     'https://www.ivoox.com/af-2x09-la-llegada-juegos-audios-mp3_rf_137070074_1.html',
        #     'https://www.youtube.com/watch?v=6nBbE4t9Ye8',
        #     'https://www.ivoox.com/1-del-jabon-al-jamon-audios-mp3_rf_55135259_1.html',
        #     'https://www.ivoox.com/2-diez-jugadores-beisbol-audios-mp3_rf_56120745_1.html',
        #     'https://www.ivoox.com/3-champagne-o-escopeta-audios-mp3_rf_57752529_1.html',
        # FIXME pytubefix https://github.com/JuanBindez/pytubefix/issues/460
        # FIXME pytubefix
        #         'https://www.youtube.com/watch?v=I-LEAM8HTjE',
        #         'https://www.youtube.com/watch?v=YPsAqRGaQYM',
        #         'https://www.youtube.com/watch?v=daeqN3eOUzo',
        #     'https://www.youtube.com/watch?v=WjYAhxWOS6o',
        #     'https://www.ivoox.com/ep03-te04-especial-trilogia-sonic-megadrive-audios-mp3_rf_144913857_1.html',
        #     'https://www.youtube.com/watch?v=pTs7m918KYQ',
        #     'https://www.youtube.com/watch?v=3J8Oc9CY-Ug',
        #     'https://www.youtube.com/watch?v=Yc3XhQ3wbws',
        #     'https://www.youtube.com/watch?v=vI5GbcKCsZs',
        #     'https://www.youtube.com/watch?v=-JdWgxEUzX4',
        #     'https://www.youtube.com/watch?v=oT_zeYbrKTs',
        #     'https://www.youtube.com/watch?v=fxLe1iAYEZg',
        #     'https://www.youtube.com/watch?v=BOCq3aXg1Z8',
        #     'https://www.youtube.com/watch?v=jtxrnVMpUL8',
        #     'https://www.ivoox.com/todo-tranquilo-dunwich-51-orquideas-siniestras-audios-mp3_rf_140823235_1.html',
        #     'https://www.ivoox.com/hab-1106-8211-guitarricadelafuente-felices-inconscientes-audios-mp3_rf_146700878_1.html',
        #     'https://www.ivoox.com/hab-1019-8211-las-hijas-felipe-sosiego-y-audios-mp3_rf_137821128_1.html',
        #     'https://www.ivoox.com/hab-1017-8211-carolina-durante-elige-tu-propia-aventura-audios-mp3_rf_137244568_1.html',
        #     'https://www.ivoox.com/hab-921-8211-dharmacide-que-telefono-no-deje-audios-mp3_rf_131800725_1.html',
        #     'https://www.ivoox.com/ck-316-shirow-ghost-in-the-shell-cyberpunk-audios-mp3_rf_146732669_1.html',
        #     'https://www.youtube.com/watch?v=aso7t0EXMS8',  #  Some Stuff I Missed, Vol. 18 (Djrum, Ceephax,
        #                                                     # Kid Spatula, Barker, Etienne De Crécy, Max Cooper...)
        #                                                     #  The Wonky Angle
        #     'https://www.youtube.com/watch?v=0-2-rq2i8oc',  # Tiger Cat by David Henry Keller - Short Stories Cafe
        #     'https://www.youtube.com/watch?v=W3roZ38fquU',  # The Wood of the Dead by Algernon Blackwood - Short Stories Cafe
        #     'https://www.youtube.com/watch?v=JWPOaPHXFbk',  # The Yellow Wallpaper by Charlotte Perkins Gilman - Short Stories Cafe
        #     'https://www.ivoox.com/el-vigilante-del-umbral-john-buchan-audios-mp3_rf_148959055_1.html',
        #     'https://www.ivoox.com/ck-317-yo-contra-barrio-double-dragon-final-audios-mp3_rf_148855264_1.html',
        #     'https://www.ivoox.com/ck-319-mangas-cortos-para-manga-corta-audios-mp3_rf_150926338_1.html',
        #     'https://www.youtube.com/watch?v=iEaTYkcv6g8',  # GGG#582: The Fifth Head of Cerberus Book Club
        #     'https://rereadingwolfe.podbean.com/e/bonus-joan-gordon-talks-about-gene-wolfe-and-chapter-6-the-master-of-the-curators-the-shadow-of-the-torturer-the-book-of-the-new-sun/',
        #     'https://rereadingwolfe.podbean.com/e/bonus-evenson-brian-1/',
        #     'https://www.ivoox.com/ck-320-dinomania-fenomeno-torno-a-parque-audios-mp3_rf_152006005_1.html',
        #     'https://www.youtube.com/watch?v=cD4qA8huyw4', #  Starting My Journey at the Iconic Bitmap Brothers Studio - Retronaut
        #     'https://www.ivoox.com/hab-907-8211-joan-tubau-corazonadas-audios-mp3_rf_127403104_1.html',
        #     'https://www.ivoox.com/gamerah-noche-a4-22-juegos-veranito-audios-mp3_rf_153170426_1.html',
        #     'https://www.youtube.com/watch?v=4EaCecxdWtI', #  Robin Hobb - Una apología de lo lento - Fronteras de Fantasia
        #     'https://www.ivoox.com/gamerah-noche-a4-23-juegos-la-audios-mp3_rf_157604512_1.html',
        #     'https://www.ivoox.com/gamerah-noche-a4-25-con-macula-audios-mp3_rf_159243708_1.html',
        #     'https://www.ivoox.com/gamerah-noche-a4-24-la-vuelta-al-audios-mp3_rf_158227485_1.html',
        #     'https://www.ivoox.com/gamerah-noche-a4-26-especial-150-en-audios-mp3_rf_160001374_1.html',
        #     'https://www.ivoox.com/gamerah-noche-a4-27-de-deportes-americanos-audios-mp3_rf_160415124_1.html',
        #     'https://www.ivoox.com/gansta-humma-especial-war-homies-infancia-audios-mp3_rf_158684787_1.html',
        #     'https://www.ivoox.com/lviii-el-enano-blanco-30-con-marneus-audios-mp3_rf_159398931_1.html',
        #     'https://www.ivoox.com/lvi-el-enano-blanco-30-con-francois-audios-mp3_rf_155694452_1.html',
        #     'https://www.ivoox.com/gamerah-noche-a4-28-esta-cancion-tiene-audios-mp3_rf_160799489_1.html',
        #     'https://www.ivoox.com/gamerah-noche-a4-29-chorrijuegos-audios-mp3_rf_161200861_1.html',
        #     'https://www.ivoox.com/gamerah-noche-a4-30-profecias-audios-mp3_rf_161561755_1.html',
        #     'https://www.ivoox.com/dados-munecos-32-dark-heresy-warhammer-40-000-audios-mp3_rf_161388816_1.html',
        #     'https://www.ivoox.com/del-parser-al-cursor-evolucion-los-audios-mp3_rf_165451626_1.html',
        #     'https://www.ivoox.com/gamerah-noche-a4-31-pistolitas-audios-mp3_rf_161997242_1.html',
        #     'https://www.ivoox.com/gamerah-noche-a4-32-la-clave-audios-mp3_rf_163356932_1.html',
        #     'https://www.ivoox.com/gmd-05x02-sonic-3-eternal-champions-audios-mp3_rf_163876304_1.html'
        #     'https://www.ivoox.com/gamerah-noche-a4-33-gabecube-audios-mp3_rf_163752026_1.html',
        #     'https://www.ivoox.com/gamerah-noche-a4-34-100-montaditos-audios-mp3_rf_164123680_1.html',
        #     'https://www.ivoox.com/gamerah-noche-a4-35-38-especial-juegos-audios-mp3_rf_164490608_1.html',
        #     'https://www.ivoox.com/gamerah-noche-a4-36-el-fantasma-de-audios-mp3_rf_166207193_1.html',
        #     'https://www.ivoox.com/rdm-12x20-nuestras-recomendaciones-2025-videojuegos-manga-audios-mp3_rf_165529804_1.html',
        #     'https://www.ivoox.com/dados-monecos-33-w40k-imperium-maledictum-el-audios-mp3_rf_162728537_1.html',
        #     'https://www.ivoox.com/dados-monecos-34-delta-green-guia-del-audios-mp3_rf_164283932_1.html',
        #     'https://www.youtube.com/watch?v=Jsx0ZPOqfS4',
        #     'https://www.youtube.com/watch?v=X130fBCU2LE'
        #     'https://www.youtube.com/watch?v=WcnvV6PFGO0',
        #     'https://www.youtube.com/watch?v=Cpi85VTcmSo',
        #     'https://www.youtube.com/watch?v=IQ7l6APecf4',
        #     'https://www.youtube.com/watch?v=TwRcOa7-qVg',
        #     'https://www.youtube.com/watch?v=rYPOqa-nUF0',
        #     'https://www.youtube.com/watch?v=SSN8ZRbtYoE',
        #     'https://www.youtube.com/watch?v=LiFVDKbYWqA',
        #     'https://www.ivoox.com/gamerah-noche-a4-40-objetos-coleccion-audios-mp3_rf_167855908_1.html',
        #     'https://www.youtube.com/watch?v=7s8F0706QwQ', # Tom Hillman new book - Pity, Power and Tolkien's Ring (and more!) - TolkienGuide
        #     'https://www.youtube.com/watch?v=02_HTdOWr5Y', #  True Detective S1 – Mythology, Folklore & The Occult - Novum
        #     'https://www.youtube.com/watch?v=dNHq_nn1m4Y', #  La musica nacida de Internet - Surfeando el nicho
        #     'https://www.youtube.com/watch?v=hLVDq8ZIM8w', # The Cult's Ian Astbury Gets Deep: Mortality, Madness & Rock Legends! -  Lipps Service
        #     'https://www.youtube.com/watch?v=ftKG6SsgtUE', # Ian Astbury on The Return of Death Cult, Billy Duffy & Defying the Music Industry - Lipps Service
            # 'https://www.ivoox.com/indieseables-4x07-el-radio-audios-mp3_rf_170147896_1.html',
            # 'https://www.ivoox.com/indieseables-4x08-homura-hime-triple-i-minishoot-audios-mp3_rf_170551608_1.html',
            # 'https://www.youtube.com/watch?v=dUimfKLKs68', #  Rick Owens on Championing Alternative Aesthetics | Fashion Neurosis Podcast with Bella Freud | Video - Fashion Neurosis
            # 'https://www.ivoox.com/podcast-cd-dynamite-headdy-audios-mp3_rf_138979652_1.html', # Cartucho Digital Podcast CD: Dynamite Headdy
            # 'https://www.ivoox.com/podcast-cd-conker-s-bad-fur-day-audios-mp3_rf_137784976_1.html', # Cartucho Digital Podcast CD: Conker´s Bad Fur Day
            # 'https://www.ivoox.com/podcast-cd-ecco-the-dolphin-audios-mp3_rf_135376262_1.html', # Cartucho Digital Podcast CD: Ecco the Dolphin
            # 'https://www.ivoox.com/aristocratas-77-comedia-gamberra-de-audios-mp3_rf_105199008_1.html', # Los Aristócratas - 77 - Comedia gamberra de los 80
            # 'https://www.ivoox.com/aristocratas-89-matusalen-audios-mp3_rf_125914394_1.html', # Los Aristócratas - 89 - Matusalén
            # 'https://www.ivoox.com/aristocratas-103-nacho-vigalondo-audios-mp3_rf_147794281_1.html', # Los Aristócratas - 103 - Nacho Vigalondo
            # 'https://www.ivoox.com/quello-che-fu-20-anos-vicisitud-audios-mp3_rf_170180689_1.html', # Quello che fu: 20 años de Vicisitud & Sordidez
            # 'https://www.ivoox.com/86-una-nueva-vale-del-ano-2000-audios-mp3_rf_140258971_1.html', # Virupodcast #86 - Una NUEVA VALE del año 2000
            # 'https://www.ivoox.com/87-leemos-comentamos-primera-novela-audios-mp3_rf_140892574_1.html', # virupodcast
            # 'https://www.ivoox.com/90-alimentos-fracasaron-1-parte-audios-mp3_rf_146544903_1.html', # virupodcast
            # 'https://www.ivoox.com/102-registrando-casa-viru-audios-mp3_rf_169913724_1.html', # virupodcast
            # 'https://www.youtube.com/watch?v=P_afLRypw6M', #  175: Tor Valenza, Writer and Senior Story Editor, Stargate SG-1 (Interview) - Dial The Gate
            # 'https://www.youtube.com/watch?v=fOzkUKJCxTw', # Lecture @ Lyle: John Carmack, Twenty Years after Doom: The future of Engineering
            # 'https://www.youtube.com/watch?v=OOVUZZr655o', # John Carmack DOOM 3 Keynote (Quakecon 2004)
            # 'https://www.youtube.com/watch?v=Q1q49GxsPWM', # John Carmack - Doom 3 Engine Technology Interview
            # 'https://www.youtube.com/watch?v=ePQs_IrJXEQ', # Christopher Judge Has One Condition for Returning as Teal'c to Stargate (Clip) - Dial the Gate
            # 'https://www.youtube.com/watch?v=sZZaAgn0YWM', #  387: Martin Gero, Creator of the Next STARGATE TV Series (Interview) - Dial the Gate
            # 'https://www.youtube.com/watch?v=n-O5QibGAfk', #  187: Edward Gross, Author, Chevrons Locked: The Unauthorized Oral History of SG-1 (Interview) - Dial the Gate
            # 'https://www.youtube.com/watch?v=QsIFOMMG2uU',
            # 'https://www.youtube.com/watch?v=kekRXOejWR4',
            # 'https://www.youtube.com/watch?v=TbTX4WGdSSE',
            # 'https://www.youtube.com/watch?v=wZ_EhnG_zq0',
            # 'https://www.youtube.com/watch?v=P0fsz8qibCU', # KLUGE: The Haphazard Construction of the Human Mind | Gary Marcus | Talks at Google
            # 'https://www.ivoox.com/cuantica-grafica-podcast-18-8211-ciencia-barbarie-audios-mp3_rf_124185493_1.html',
            # 'https://www.ivoox.com/cuantica-grafica-podcast-14-8211-2023-audios-mp3_rf_121748381_1.html',
            # 'https://www.ivoox.com/cuantica-grafica-podcast-13-asalto-a-la-audios-mp3_rf_120854446_1.html',
            # 'https://www.ivoox.com/mv-27-los-mejores-comics-infantiles-2025-audios-mp3_rf_167187113_1.html',
            # 'https://www.ivoox.com/mv25-comics-perretes-para-peques-audios-mp3_rf_161156968_1.html',
            # 'https://www.ivoox.com/mv-20-los-mejores-comics-infantiles-2024-audios-mp3_rf_137811379_1.html',
            # 'https://www.ivoox.com/mv-18-halloween-comics-fantasmales-audios-mp3_rf_135402897_1.html',
            # 'https://www.ivoox.com/mv-17-parque-infantil-jurasico-audios-mp3_rf_134329643_1.html',
            # 'https://www.ivoox.com/mv-16-comics-sobre-coles-ii-audios-mp3_rf_132684483_1.html',
            # 'https://www.ivoox.com/mv-15-comics-nuestra-infancia-para-peques-de-audios-mp3_rf_132526842_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-01-juegos-lucha-audios-mp3_rf_168294183_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-02-acierta-detras-viii-audios-mp3_rf_168696414_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-03-mas-paella-mas-toros-audios-mp3_rf_169169488_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-04-moviles-audios-mp3_rf_169586738_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-05-segundones-audios-mp3_rf_170001423_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-06-parlamento-audios-mp3_rf_170405072_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-07-mierdandising-audios-mp3_rf_170807627_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-08-club-lectura-audios-mp3_rf_171211473_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-09-juegos-pendientes-y-audios-mp3_rf_172013138_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-10-historias-audios-mp3_rf_172441480_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-11-dragones-rosas-audios-mp3_rf_172847350_1.html',
            # 'https://www.youtube.com/watch?v=-wNiGlssQsc',
            # 'https://www.youtube.com/watch?v=zykdF9GuMok',
            # 'https://www.ivoox.com/urgente-mensaje-prioritario-flota-estelar-audios-mp3_rf_177914859_1.html',
            # 'https://www.youtube.com/watch?v=ccchYpiHmjo',
            # 'https://www.ivoox.com/354-all-new-resenotron-n-7-ricardo-audios-mp3_rf_177914304_1.html',
            # 'https://www.ivoox.com/retropartidas-2x19-castle-of-illusion-master-system-audios-mp3_rf_177663705_1.html'
            # 'https://www.ivoox.com/gamerah-noche-a5-10-historias-audios-mp3_rf_172441480_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-11-dragones-rosas-audios-mp3_rf_172847350_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-12-comics-audios-mp3_rf_173295551_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-13-diselo-a-cubitorah-audios-mp3_rf_173701210_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-14-miscelanea-noche-audios-mp3_rf_174116781_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-15-juegos-pc-audios-mp3_rf_174516012_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-16-recomendaciones-pero-no-audios-mp3_rf_174970371_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-17-blasfemias-audios-mp3_rf_175376816_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-18-club-lectura-audios-mp3_rf_175828432_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-19-especial-mundial-audios-mp3_rf_176258176_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-20-acierta-detras-audios-mp3_rf_177047637_1.html',
            # 'https://www.ivoox.com/gamerah-noche-a5-21-tiempo-calippo-audios-mp3_rf_177408834_1.html',
            # 'https://www.youtube.com/watch?v=ydIRV7XiP9A',
            # 'https://www.youtube.com/watch?v=SAUlrOlcKfY',
            # 'https://www.ivoox.com/milenio-3-viaje-a-misterios-del-neolitico-gobleki-audios-mp3_rf_3361811_1.html'
            # 'https://www.youtube.com/watch?v=7psgKayzrUE',
            # 'https://www.youtube.com/watch?v=lyPLWnEObKo',
            # 'https://www.youtube.com/watch?v=6_g8d6v6hb0',
            # 'https://www.youtube.com/watch?v=-x4jE_s72cg',
            # 'https://www.youtube.com/watch?v=Bq_131WvOUs',
            'https://www.ivoox.com/gamerah-noche-a5-22-el-regreso-del-audios-mp3_rf_180339497_1.html',
            'https://www.ivoox.com/gamerah-noche-a5-23-bunker-king-audios-mp3_rf_180748325_1.html',
        ]
    for result in podcasts.download_episodes(episode_list):
        if result.error:
            print(f'Error - {result.url} - {result.error}')
        elif result.skipped:
            print(f'Ya descargado - {result.url}')
