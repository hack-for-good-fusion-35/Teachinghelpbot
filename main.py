from flask import Flask, render_template
import logging
from flask_socketio import SocketIO, emit
from chatterbot import ChatBot
async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def main():
    return render_template('index.html')


def init():
    logging.basicConfig(filename='Bot.log', filemode='w',
                        format='[%(name)s][%(levelname)s][%(message)s]', level=logging.DEBUG)
    logging.debug("Bot initilization started...")


@socketio.on('ChatMessage', namespace='/chatbot')
def chatMessages(message):
    logging.debug("Message received = %s", message)
    message = message.strip()

    try:
        parts = message.split(":")
        firstPart = parts[0]
        firstPart = firstPart.strip()
        logging.debug("First part=%s", firstPart)
        bot = ChatBot(
            'Feedback Learning Bot',
            storage_adapter='chatterbot.storage.SQLStorageAdapter',
            logic_adapters=[
                {
                    'import_path': 'chatterbot.logic.BestMatch'
                },
                {
                    'import_path': 'chatterbot.logic.LowConfidenceAdapter',
                    'threshold': 0.65,
                    'default_response': 'I am sorry, I am new to it.'
                }
            ],
            input_adapter='chatterbot.input.VariableInputTypeAdapter',
            output_adapter='chatterbot.output.TerminalAdapter'
        )
        logging.debug("Inside Bot processing")
        CONVERSATION_ID = bot.storage.create_conversation()
        input_statement = bot.input.process_input_statement(firstPart)
        statement, response = bot.generate_response(
            input_statement, CONVERSATION_ID)
        if firstPart.lower() == "tquestion":
            logging.debug("Saving answer")
            question = parts[1]
            logging.debug("question=%s", question)
            question_statement = bot.input.process_input_statement(question)
            try:
                AnsTag = parts[2]
                if AnsTag.lower() == "tanswer":
                    AnsTag = AnsTag.strip()
                    logging.debug("AnsTag=%s", AnsTag)
                    Answer = parts[3]
                    Answer = Answer.strip()
                    if Answer:
                        logging.debug("Answer=%s", Answer)
                        answer_statement = bot.input.process_input_statement(
                            Answer)
                        bot.learn_response(
                            answer_statement, question_statement)
                        bot.storage.add_to_conversation(
                            CONVERSATION_ID, question_statement, answer_statement)
                        bot.output.process_response(answer_statement)
                        emit("Bot_Reply", "Saved your answer.")
                else:
                    emit("Bot_Reply", "Answer tag is incorrect")
            except:
                emit("Bot_Reply", "No Answer found for question")
        else:
            logging.debug("Response=%s", response.text)
            emit("Bot_Reply", response.text)
    except:
        logging.debug("something is not good")
        emit("Bot_Reply", "something is not good")


if __name__ == "__main__":
    init()
    logging.debug("Socket started...")
    socketio.run(app, host='127.0.0.1', port=1805)
