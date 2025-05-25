################################################## SETTING ##################################################

#importa librerie
import os
import time
import pydub
import openai
import pygame
import librosa
import numpy as np
from gtts import gTTS
import soundfile as sf
import sounddevice as sd
import speech_recognition as sr

#chiave API di OpenAI
openai.api_key = '
#api_key here
'

#paths
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
generic_audio_path = os.path.join(desktop_path, "generic_audio.wav")










################################################## LOGIN ##################################################

#crea un array vuoto e carica all'interno username e password del file
def load_unp_in_array(unp_path):
    unp_array = []
    with open(unp_path, 'r', encoding='utf-8', errors='ignore') as unp_file:
        unp_lines = unp_file.readlines()
        for unp_line_idx in range(0, len(unp_lines), 2):
            username_from_file = unp_lines[unp_line_idx].strip()
            password_from_file = unp_lines[unp_line_idx+1].strip()
            unp_array.append((username_from_file, password_from_file))
    return unp_array

#controlla se username_input è presente nel file: se lo è confronta l'onda vocale e identifica l'utente e ne effettua il login, altrimenti blocca l'account che stava per essere violato
def username_check(unp_array):
    create_audio()
    pron_username = text_to_speech('Pronuncia il tuo username', 'omnibot_voice.wav')
    play_wav(pron_username)
    record_audio(generic_audio_path)
    generated_text_username = transcribe_audio(generic_audio_path)
    renamed_audio_path = os.path.join(desktop_path, (generated_text_username.lower() + '_ref_audio.wav'))
    if os.path.exists(renamed_audio_path):
        db_features = extract_features(renamed_audio_path)
        new_features = extract_features(generic_audio_path)
        distancee = identify_speaker(db_features, new_features, 100)
        if distancee:
            pron_persid = text_to_speech('La persona è stata identificata', 'omnibot_voice.wav')
            play_wav(pron_persid)
        else:
            time_block = 5
            pron_persnonid = text_to_speech(('La persona non è stata identificata. Per questioni di sicurezza l\'account di ' + generated_text_username + ' è stato bloccato per ' + str(time_block) + ' minuti'), 'omnibot_voice.wav')
            play_wav(pron_persnonid)
            time.sleep(time_block*60)
        os.remove(generic_audio_path)
    else:
        os.rename(generic_audio_path, renamed_audio_path)
    username_input = generated_text_username
    username_latest = 'default'
    for username_from_file, password_from_file in unp_array:
        if username_input == username_from_file:
            username_latest = username_input
            create_audio()
            pron_password = text_to_speech('Pronuncia la tua password', 'omnibot_voice.wav')
            play_wav(pron_password)
            record_audio(generic_audio_path)
            generated_text_password = transcribe_audio(generic_audio_path)
            password_input = generated_text_password
            tent_rim=3                                                                       #tentativi rimasti modificabili a piacimento in base alle necessità
            while 1<=tent_rim<=float('inf'):
                if password_from_file == password_input:
                    pron_benvenuto = text_to_speech(('Ciao ' + username_input + ', benvenuto in OmniBot!'), 'omnibot_voice.wav')
                    play_wav(pron_benvenuto)
                    os.remove(generic_audio_path)
                    get_username_file_path(username_input)
                    break
                else:
                    if tent_rim>1 and tent_rim-1!=1:
                        pron_passworderr = text_to_speech(('Password errata, ' + str(tent_rim-1) + ' tentativi rimasti'), 'omnibot_voice.wav')
                        play_wav(pron_passworderr)
                        tent_rim=tent_rim-1
                        os.remove(generic_audio_path)
                        create_audio()
                        record_audio(generic_audio_path)
                        generated_text_password = transcribe_audio(generic_audio_path)
                        password_input = generated_text_password
                    elif tent_rim==2:
                        pron_passworderr = text_to_speech(('Password errata, un tentativo rimasto'), 'omnibot_voice.wav')
                        play_wav(pron_passworderr)
                        tent_rim=tent_rim-1
                        os.remove(generic_audio_path)
                        create_audio()
                        record_audio(generic_audio_path)
                        generated_text_password = transcribe_audio(generic_audio_path)
                        password_input = generated_text_password
                    elif tent_rim==1:
                        time_block = 5
                        pron_passworderr = text_to_speech(('Password errata, ' + username_input + ' bloccato per ' + str(time_block) + ' minuti'), 'omnibot_voice.wav')
                        play_wav(pron_passworderr)
                        time.sleep(time_block*60)
            break
    return username_latest, username_input, renamed_audio_path

#restituisce username del utente loggato, eventualmente creandolo se non c'è già
def get_actual_logged_username():
    unp_path = 'unp.txt'
    unp_array = load_unp_in_array(unp_path)
    username_check_results = username_check(unp_array)
    username_latestt = username_check_results[0]
    username_inputt = username_check_results[1]
    renamed_audio_pathh = username_check_results[2]
    i=False
    while username_latestt == 'default':
        if i==False:
            create_audio()
            pron_accnonpres = text_to_speech('Username non presente, vuoi creare un nuovo account? Sì o no?', 'omnibot_voice.wav')
            play_wav(pron_accnonpres)
            record_audio(generic_audio_path)
            generated_text_yorn = transcribe_audio(generic_audio_path)
            yorn = generated_text_yorn
            os.remove(generic_audio_path)
        if yorn.lower()=='sì':
            new_account_username = username_inputt
            username_latestt = new_account_username
            create_audio()
            pron_password = text_to_speech('Pronuncia la tua password', 'omnibot_voice.wav')
            play_wav(pron_password)
            record_audio(generic_audio_path)
            generated_text_password = transcribe_audio(generic_audio_path)
            new_account_password = generated_text_password
            pron_benvenuto = text_to_speech(('Ciao ' + new_account_username + ', benvenuto in OmniBot!'), 'omnibot_voice.wav')
            play_wav(pron_benvenuto)
            os.remove(generic_audio_path)
            with open(unp_path, 'a', encoding='utf-8', errors='ignore') as unp_file:
                unp_file.write(new_account_username + '\n' + new_account_password + '\n')
                unp_file.close()
            break
        elif yorn=='no':
            pron_riprova = text_to_speech('Riprova', 'omnibot_voice.wav')
            play_wav(pron_riprova)
            os.remove(renamed_audio_pathh)
            username_check_results = username_check(unp_array)
            username_latestt = username_check_results[0]
            username_inputt = username_check_results[1]
            renamed_audio_pathh = username_check_results[2]
            i=False
        else:
            create_audio()
            pron_dontund = text_to_speech('Non ho capito bene', 'omnibot_voice.wav')
            play_wav(pron_dontund)
            record_audio(generic_audio_path)
            generated_text_yorn = transcribe_audio(generic_audio_path)
            yorn = generated_text_yorn
            os.remove(generic_audio_path)
            i=True
    actual_logged_username = username_latestt
    return actual_logged_username

#ottiene username file path in cui salvare i dati dell'utente
def get_username_file_path(username_inputt):
    username_file_path = os.path.join(desktop_path, (username_inputt.lower() + '_history.txt'))
    if os.path.exists(username_file_path):
        pass
    else:
        with open(username_file_path, 'w', encoding='utf-8', errors='ignore') as file:
            file.write('Come ti chiami?\nMi chiamo OmniBot.\nQual è il tuo nome?\nIl mio nome è OmniBot.\nChi ti ha creato?\nDaniele e Leonardo.')                    #domande e risposte predefinite
    return username_file_path

#salva i dati dell'utente
def save_data(qna_arrayy, username_file_pathhh):
    with open(username_file_pathhh, 'w') as file:
        for question_from_filee, answer_from_file in qna_arrayy:
            file.write(f"{question_from_filee}\n{answer_from_file}\n")

#crea audio del nuovo account
def create_audio():
    sample_rate = 44100
    duration = 5
    frequency = 440
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio_data = (0.5 * np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16).tobytes()

    audio_segment = pydub.AudioSegment(
        audio_data,
        sample_width=2,
        frame_rate=sample_rate,
        channels=1                                                                                     #1=mono e 2=stereo
    )
    audio_segment.export(generic_audio_path, format="wav")

#registra sovrascrivendo all'audio appena creato
def record_audio(generic_audio_path, duration=5, sample_rate=44100):
    audio_data = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()
    sf.write(generic_audio_path, audio_data.squeeze(), sample_rate)

#trascrive l'audio
def transcribe_audio(generic_audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(generic_audio_path) as source:
        audio_data = recognizer.record(source)
    try:
        result = recognizer.recognize_google(audio_data, show_all=True, language='it-IT')
        if 'alternative' in result:
            main_transcript = max(result['alternative'], key=lambda x: x.get('confidence', 0.0))['transcript']
            return main_transcript
        else:
            print("Google Web Speech API non ha potuto riconoscere l'audio.")
            return None
    except sr.UnknownValueError:
        print("Google Web Speech API non ha potuto riconoscere l'audio.")
        return None
    except sr.RequestError as e:
        print(f"Errore nella richiesta a Google Web Speech API: {e}")
        return None
    
#estrae le features dall'audio
def extract_features(file_path):
    audio_data, _ = librosa.load(file_path, sr=None)
    mfccs = librosa.feature.mfcc(y=audio_data, sr=44100, n_mfcc=13)
    return np.mean(mfccs, axis=1)

#identifica chi parla
def identify_speaker(db_features1, new_features1, threshold):
    distance = np.linalg.norm(db_features1 - new_features1)
    return distance < threshold

#text-to-speech
def text_to_speech(text, speech, lang='it'):
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(speech)
    return speech

#riproduce l'audio
def play_wav(speech1):
    pygame.init()
    pygame.mixer.init()
    sound = pygame.mixer.Sound(speech1)
    sound.play()
    pygame.time.wait(int(sound.get_length()*1000))
    pygame.mixer.quit()










################################################## RISPOSTA ##################################################

#crea un array vuoto e carica all'interno le domande e le risposte del file
def load_qna_in_array(username_file_path):
    qna_array = []
    with open(username_file_path, 'r', encoding='utf-8', errors='ignore') as qna_file:
        qna_lines = qna_file.readlines()
        for qna_line_idx in range(0, len(qna_lines), 2):
            question_from_file = qna_lines[qna_line_idx].strip()
            answer_from_file = qna_lines[qna_line_idx+1].strip()
            qna_array.append((question_from_file, answer_from_file))
    return qna_array

#controllo della domanda
def get_answer_from_file(domanda):
    for question_from_file, answer_from_file in qna_array:
        if domanda.lower() in question_from_file.lower():
            return answer_from_file
    return None

#risposta finale data dall'unione del file history utente e OpenAI
def get_final_answer(domanda):
    answer_from_file = get_answer_from_file(domanda)
    prompt = "\n".join([f"{question_from_filee}: {answer_from_file}" for question_from_filee in qna_array])
    prompt += f'Domanda: {domanda}\nRisposta:'
    richiesta = openai.Completion.create(
    engine="text-davinci-003",
    prompt=prompt,
    temperature=0.9,
    max_tokens=1000
    )
    
    return richiesta.choices[0].text.strip()










################################################## ESECUZIONE ##################################################

#esegue OmniBot
login_bool = False
question_pronunced = False
while True:
    if login_bool == False:
        actual_logged_usernamee = get_actual_logged_username()
        login_bool = True

    if question_pronunced == False:
        pron_question = text_to_speech('Pronuncia la tua domanda', 'omnibot_voice.wav')
        play_wav(pron_question)
        question_pronunced = True
    create_audio()
    record_audio(generic_audio_path)
    generated_text_question = transcribe_audio(generic_audio_path)
    os.remove(generic_audio_path)
    question_input = generated_text_question
    if question_input.lower() == 'arrivederci':
        pron_bye = text_to_speech(('Arrivederci ' + actual_logged_usernamee + '!'), 'omnibot_voice.wav')
        play_wav(pron_bye)
        break
    
    username_file_pathh = get_username_file_path(actual_logged_usernamee)
    qna_array = load_qna_in_array(username_file_pathh)
    final_answer = get_final_answer(question_input)
    pron_finansw = text_to_speech(final_answer, 'omnibot_voice.wav')
    play_wav(pron_finansw)
    qna_array.append((question_input, final_answer))
    save_data(qna_array, username_file_pathh)
