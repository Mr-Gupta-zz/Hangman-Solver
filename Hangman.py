#Author: Amritansh Gupta
#Date: 11/13/18
#Hulu Internship Challenge
import requests
from collections import defaultdict
import string
import random
import time

#Game class to keep track of the progress
class Game:
    def __init__(self, puzzle, token):

        #token for request
        self.token = token

        self.puzzle = puzzle

        #the separate words in the phrase
        self.words_in_phrase = self.getWords()
        #chanes left to play with
        self.chances = 3

    #to update the game after every move
    def updatePuzzle(self, puzz, chance):
        self.puzzle = puzz

        self.chances = chance
        self.words_in_phrase = self.getWords()
    #Splits the phrase to get words
    def getWords(self):
        return self.puzzle.split(' ')


class AI:
    def __init__(self, game, words):
        self.game = game

        #Most used letters in english dictionary in descending order
        self.firstLetts = ['U','L','D','R','H','S','N','I','O','A','T','E']

        #Words from the custom wordlist for the AI
        self.words_list = words

        #Our domain for letters available
        self.range_letts = list(string.ascii_uppercase)

    #Main prediction function
    def predict(self):

        #Guess some first letters according to the most used letters listself.
        #Move to more concrete checks if get one wrong
        if len(self.firstLetts) > 0 and game.chances == 3:

            elem = self.firstLetts[-1]
            del self.firstLetts[-1]
            #print(elem, self.range_letts)

            self.range_letts.remove(elem)
            return elem

        else:

            #Get the guesses for words
            considerations = self.processWords()

            #Have to go random if no predictions
            if len(considerations) == 0:
                if len(self.firstLetts) > 0:
                    elem = self.firstLetts[-1]
                    del self.firstLetts[-1]
                    while elem not in self.range_letts and len(self.firstLetts) > 0:
                        elem = self.firstLetts[-1]
                        del self.firstLetts[-1]
                    self.range_letts.remove(elem)
                    return elem

                print("No matching words found in word list, choosing at random")
                elem = random.choice(self.range_letts)
                while elem not in self.range_letts:
                    elem = random.choice(self.range_letts)
                self.range_letts.remove(elem)
                return elem

            #Getting the most frequent letters from all word predictions
            freq_map = self.letterFrequencies(considerations)
            #Sorting them by largest frequency
            sorted_freq = sorted(freq_map.items(), key=lambda x:x[1], reverse=True)

            l = sorted_freq.pop(0)[0]

            #Use letter if not already used
            while l not in self.range_letts and len(sorted_freq)>0:
                l = sorted_freq.pop(0)[0]

            #Shortening the domain
            self.range_letts.remove(l[0])

            return l

    #Parses individual words in phrases and matches to words from word list
    def processWords(self):
        considerations = []

        #For each word in the puzzle phrase
        for word in self.game.words_in_phrase:
            if '_' not in word:
                continue

            #Get words only that are the same length as the individual word
            word_options = self.getSameLengthWords(word)

            #Mapping the letters to their indexes in the word
            letter_map = self.getLetters(word)
            #Dont need the unfilled ones
            del letter_map['_']

            #Adding to considerations
            temp = ([w for w in word_options if self.matchPosition(w, letter_map)])
            considerations += temp

        return considerations

    #Comparing our same length words to required one
    #Logic- If the word is to satrisfy the condition, all the letters in our original,
    #       word needs to have the letters in the same positions as the one being
    #       considered
    def matchPosition(self, word_to_consider, positions):

        #Splitting the word to the letters
        word_to_consider = list(word_to_consider)

        #Checking the letters by index
        for letter in positions:
            for ind in positions[letter]:
                #Not a possible word if any index doesnt match
                if word_to_consider[ind] != letter:
                    return False
                #Mark the letter as seen
                word_to_consider[ind] = '-'
            #if extra letters left in the word to consider, its not the one we want
            if letter in word_to_consider:
                return False

        return True
    #Return a map of letters and their frequency
    def letterFrequencies(self, words):
        freqs = defaultdict(int)
        for word in words:
            for l in word:
                freqs[l] += 1
        return freqs

    #Returns a map of letters and their indices in the word
    def getLetters(self, word):
        map = defaultdict(list)
        for index,value in enumerate(word):
            map[value].append(index)
        return map

    #Gets words of the same length from the word_list
    def getSameLengthWords(self,word):
        return [w for w in self.words_list if len(w) == len(word)]


#Starting the main game here
print("Starting Hangman")

#Getting the words from the dictionary
def getWords():
    lis = []
    with open('word_list1.txt') as f:
        for word in f:
            lis.append(word.strip())
    return lis

dictionary = getWords()

#Looping until interrupted
while True:
    try:
        #New game after 3 seconds of previous one
        print("Starting next game in 3 seconds")
        time.sleep(3)

        #requesting a Game
        request = requests.get('http://gallows.hulu.com/play?code=amritanshgupta@gmail.com').json()
        print("Begin:",request['state'],"\n")

        game = Game(request['state'], request['token'])
        remaining_guesses = request['remaining_guesses']
        status = 'ALIVE'
        #Initiating the AI
        ai = AI(game, dictionary)

        #While the game is in the active status
        while status == 'ALIVE':
            #make a guess
            guess = ai.predict()

            print("Guessing ", guess)

            params = {'token': game.token,
                      'guess':guess}
            play = requests.post(url='http://gallows.hulu.com/play?code=amritanshgupta@gmail.com',data=params).json()

            print(play['state'], "Chances left:", play['remaining_guesses'])

            status = play['status']
            #updating the puzzle
            game.updatePuzzle(play['state'], play['remaining_guesses'])
            if status != 'ALIVE':
                print("Youre ", status)
    except KeyboardInterrupt:
        print("\n\nThank you for testing the AI!")
        quit()
