import nltk
from nltk.stem import WordNetLemmatizer
import pickle
import numpy as np
from keras.models import load_model
from tkinter import *
import json
import random

lemmatizer = WordNetLemmatizer()
modell = load_model('chatbot_model.h5')
intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))


def clean_up_sentence(sentence):
    # tokenize the pattern - split wrds into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


# return bag of wrds array: 0 or 1 for each word in the bag that exists in the sentence


def bow(sentence, wrds, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of wrds - matrix of N wrds, vocabulary matrix
    bag = [0] * len(wrds)
    for s in sentence_words:
        for i, w in enumerate(wrds):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)


def predict_class(sentence, modelll):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = modelll.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def get_response(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result


def chatbot_response(msg):
    ints = predict_class(msg, modell)
    res = get_response(ints, intents)
    return res


# Creating GUI with tkinter
base = Tk()
base.title("ENSABOT")
base.geometry("400x500")
base.resizable(width=FALSE, height=FALSE)
base.iconbitmap(default="icon.ico")
base.config(background='#4C4A48')


# noinspection PyUnusedLocal,DuplicatedCode
def click(self):
    msg = EntryBox.get("1.0", 'end-1c').strip()
    EntryBox.delete("0.0", END)

    if msg != '':
        ChatLog.config(state=NORMAL)
        ChatLog.insert(END, 'YOU: ' + msg + '\n\n')
        ChatLog.config(foreground="black", font=("Courier", 14))

        res = chatbot_response(msg)
        ChatLog.insert(END, "ENSABOT: " + res + '\n\n')

        ChatLog.config(state=DISABLED)
        ChatLog.yview(END)


base.bind('<Return>', click)


# noinspection PyUnusedLocal,DuplicatedCode
def send():
    msg = EntryBox.get("1.0", 'end-1c').strip()
    EntryBox.delete("0.0", END)

    if msg != '':
        ChatLog.config(state=NORMAL)
        ChatLog.insert(END, 'YOU: ' + msg + '\n\n')
        ChatLog.config(foreground="black", font=("Courier", 14))

        res = chatbot_response(msg)
        ChatLog.insert(END, "ENSABOT: " + res + '\n\n')

        ChatLog.config(state=DISABLED)
        ChatLog.yview(END)


# Create Chat window
ChatLog = Text(base, bg="#48c7ad", highlightbackground="#4C4A48",
               highlightthickness=2, bd=0, height="8", width=50, font="Arial", wrap=WORD)
ChatLog.config(state=DISABLED)

# Bind scrollbar to Chat window
scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="arrow", bg='#713199')
ChatLog['yscrollcommand'] = scrollbar.set

# Create Button to send message
SendButton = Button(base, text="Send", bg='black', borderwidth=5, highlightbackground="black",
                    highlightthickness=2, font=("Courier", 12, 'bold'), width="12",
                    height=5, bd=0, fg='#ffffff', command=send)

# Create the box to enter message
EntryBox = Text(base, bd=0, bg="#48c7ad", highlightbackground="#4C4A48",
                highlightthickness=2, width=29, height="5", font="Courier")
EntryBox.focus_set()

# Place all components on the screen
scrollbar.place(x=376, y=6, height=386)
ChatLog.place(x=6, y=6, height=386, width=370)
EntryBox.place(x=6, y=401, height=90, width=265)
SendButton.place(x=260, y=401, height=90)

base.mainloop()
