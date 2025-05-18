import speech_recognition as sr
import pyttsx3 
from utils.singleton import Singleton
from utils.debugOptions import DebugOptions
import sounddevice as sd
import os
import re
from time import sleep

class SpeechToText(Singleton):
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return  # Prevent re-initialization
        self.__recognizer = sr.Recognizer()
        self.__micIdx = self.__selectKnownMic("FIFINE K669 Microphone")
        self.__recognizer.vosk_model = self.__findVosk()
        self.__trueMicIdx = None

        self._initialized = True


    def __selectKnownMic(self, mic_name):
        optionals = []
        mic_pattern = re.compile(rf"{mic_name}")
        for mic in sd.query_devices():
            if re.search(mic_pattern, mic['name']):
                optionals.append(mic['index'])
        if not optionals:
            return [self.__defaultMic()]
        return optionals
        
    def __defaultMic(self):
        mic_pattern = re.compile(r'Microsoft Sound Mapper - Input')
        for mic in sd.query_devices():
            if re.search(mic_pattern, mic['name']):
                if DebugOptions() != "off":
                    print(f"USING DEFAULT: {mic['name']}")
                return mic['index']

    def __selectMic(self) -> int:
        mics = dict()
        for i, mic in enumerate(sd.query_devices()):
            try:
                sd.default.device = (i, None)  # (input, output)
                sd.check_input_settings()
                mics[mic['name']] = i
            except Exception as e:
                pass
        if len(mics.keys()) > 1:
            selections = ""
            for i, mic in enumerate(mics.keys()):
                selections += (f"{i+1}) {mic}\n")
            while True:
                print(f"Select the wanted input device:\n{selections}")
                user = str(input(f"your selection (1-{len(mics)}) >> "))
                if user.isdigit():
                    if 0 < int(user) <= len(mics): return mics[list(mics.keys())[int(user)-1]]
                    else: continue
        
        elif len(mics.keys()) == 1:
            return list(mics.values())[0]
        
        return -1
    
    def __findVosk(self) -> str:
        founds = []
        for item in os.listdir():
            if os.path.isdir(item) and item.startswith("vosk"):
                founds.append(item)

        if len(founds) > 1:
            selections = ""
            for i, m in enumerate(founds):
                selections += (f"{i+1}) {m}\n")
            while True:
                print(f"Select the right Vosk model:\n{selections}")
                user = str(input(f"your selection (1-{len(founds)}) >> "))
                if user.isdigit():
                    if 0 < int(user) <= len(founds): return founds[int(user)-1]
                    else: continue
        elif len(founds) == 1:
            return founds[0]

        return ""

    def listen(self, org="google", lang="en-US", default_msg="") -> str:
        text = ""       
        if self.__trueMicIdx:
            self.__micIdx = [self.__trueMicIdx]

        mic_idx = 0
        while True:
            try:
                with sr.Microphone(device_index=self.__micIdx[mic_idx]) as source:
                    if DebugOptions() != "off":
                        print("Ajusting mic for ambient noise....")
                    self.__recognizer.adjust_for_ambient_noise(source, duration=1)
                    print(f"say 'default' to use default message '{default_msg}'")
                    sleep(0.5)
                    print("\n--- SPEAK NOW!--- \n")
                    audio = self.__recognizer.listen(source, timeout=5, phrase_time_limit=8)
                    match org.lower():
                        case "google":
                            text =  self.__recognizer.recognize_google(audio, language=lang)
                        case "vosk":
                            text = self.__recognizer.recognize_vosk(audio)
                        case _:
                            raise ValueError(f"Provider {org} is not supported.")
                
                print("Recognized STT: ", text)
                self.__trueMicIdx = source.device_index
                if text == "default":
                    return default_msg
                break

            except sr.RequestError as e:
                print("Could not request results; {}".format(e))
            except ValueError as e:
                print(e)
                print("Exiting...")
                exit(555)
            except sr.WaitTimeoutError as e:
                raise(e)
            except Exception as e:
                print("Error while trying to listen. Changing microphone...")
                mic_idx += 1
                if mic_idx >= len(self.__micIdx):
                    mic_idx = 0
                    self.__micIdx = [self.__defaultMic()]

        return text