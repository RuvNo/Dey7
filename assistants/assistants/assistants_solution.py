import os
import sys
import time

from openai import OpenAI

OPENAPI_KEY = 'OPENAPI_KEY'
OPENAPI_KEY_DEFAULT = 'no_key_provided'


def mock_thread_history(thread_id):
    openai_client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content="""
                    Hat die "XBO_1000_W_HS_OFR" eine Lebensdauer von mehr als 2000 Stunden?
                    """
    )
    openai_client.beta.threads.messages.create(
        thread_id=thread_id,
        role="assistant",
        content="""
                    Nein, da die "XBO 1000 W/HS OFR" genau eine Lebensdauer von 2000 Stunden hat. Dies ist somit nicht mehr als 2000 Stunden (2000 > 2000 = false)【4:0†source】.
                    """
    )
    openai_client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content="""
                    Hat die "XBO_6000_W_HS_XL_OFR" eine Leistung von weniger als 6000 Watt?
                    """
    )
    openai_client.beta.threads.messages.create(
        thread_id=thread_id,
        role="assistant",
        content="""
                    Nein, da die "XBO_6000_W_HS_XL_OFR" genau eine Lebensdauer von 6000 Watt (W) hat. Dies ist somit nicht weniger als 6000 W (6000 < 6000 = false)【4:0†source】.
                    """
    )
    openai_client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content="""
                    Hat die "XBO_4000_W_HS_XL_OFR" einen Nennstrom von mehr als 100 A?
                    """
    )
    openai_client.beta.threads.messages.create(
        thread_id=thread_id,
        role="assistant",
        content="""
                    Ja, da die "XBO_4000_W_HS_XL_OFR" einen Nennstrom von 135 A hat. Dies ist somit mehr als 100 A (135 > 100 = true)【4:0†source】.
                    """
    )


def create_vector_store(client):
    vector_store = client.beta.vector_stores.create(name="Product_Information_Store")

    dir = "source_files"
    file_paths = [os.path.join(dir, filename) for filename in os.listdir(dir) if os.path.isfile(os.path.join(dir, filename))]
    file_streams = [open(path, "rb") for path in file_paths]
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )

    return vector_store


def create_new_assistant(client):
    vector_store = create_vector_store(client)
    assistant = client.beta.assistants.create(
        name="Osram Short-Arc-Lamps Expert",
        instructions="""
        You are an expert for Short-Arc-Lamps of the type 'XBO' from the company 'Osram'.
        You can access information regarding the different types of lamps from the associated files in the 'Product_Information_Store'.
        Each file in the store represents one type of lamp with its own characteristics.
        To answer the users questions, you are advised to search the store if applicable.
        Think step by step - Always check one file for the characteristics defined in the question before going to the next file.
        Always consider ALL 21 files in the 'Product_Information_Store' while answering.
        When asked a question, write and run code if necessary to answer it.
        Remember, in German "mehr als X h" means "> X h". "weniger als X h" means "< X h".
        When asked for the "Lebensdauer" of something, DO NOT CONSIDER the "Service Warranty Lifetime".
        """,
        tools=[{"type": "file_search"}, {"type": "code_interpreter"}],
        model="gpt-4o",
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )

    print("Successfully created a new assistant!")
    time.sleep(1)

    return assistant


def handle_failed_assistant_id_input(assistant_id, client):
    print(f"Sorry, no assistant found for id {assistant_id}")
    time.sleep(1)
    user_input_is_try_again = input("Do you want to try again with a different id?\n(y/n) ")
    time.sleep(1)
    if user_input_is_try_again == 'y':
        return ''
    else:
        print("Creating a new assistant for you...")
        assistant = create_new_assistant(client)
        return assistant.id


def get_assistant_id(client):
    assistant_id = ''
    user_input_has_assistant_id = input("Do you want to use your own assistant_id?\n(y, n) ")
    time.sleep(1)
    if user_input_has_assistant_id != 'y':
        print("Creating a new assistant for you...")
        assistant = create_new_assistant(client)
        return assistant.id

    print("Okay. Then I am going to need an Assistant ID from you.")
    while assistant_id == '':
        user_input_id = input("ID: ")

        if user_input_id != '':
            assistants = client.beta.assistants.list(order="desc")
            assistants = [a for a in assistants.data]
            assistant = [a for a in assistants if a.id == user_input_id]
            if len(assistant) > 0:
                assistant_id = assistant[0].id
            else:
                assistant_id = handle_failed_assistant_id_input(assistant_id, client)
        else:
            assistant_id = handle_failed_assistant_id_input(assistant_id, client)

    return assistant_id


if __name__ == '__main__':
    open_ai_api_key = os.getenv(OPENAPI_KEY, OPENAPI_KEY_DEFAULT)

    if open_ai_api_key == OPENAPI_KEY_DEFAULT:
        print("Sorry, but you do not seem to have set a OPENAI API Key. Please restart the docker with\n'docker run -e OPENAPI_KEY=your_api_key'")
    else:
        try:
            openai_client = OpenAI(api_key=open_ai_api_key)
            thread = openai_client.beta.threads.create()

        except:
            print(
                f"Sorry, but it seems like your OPENAI API Key {open_ai_api_key} is invalid. Please try a different key when restarting the docker with\n'docker run -e OPENAPI_KEY=your_api_key'")
            sys.exit()

        print("Welcome to my little experimental chatbot :)")
        time.sleep(1)

        try:
            openai_assistant_id = get_assistant_id(openai_client)
            print(f"Assistant Id: {openai_assistant_id}")

            finished = False

            print("\n\nHello there...")
            time.sleep(1)
            print("...and welcome to our little chat session")
            time.sleep(1)
            user_input_question = input("What is your question?\nQuestion: ")
            print("...thinking...")

            mock_thread_history(thread.id)

            while not finished:
                message = openai_client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=user_input_question
                )

                with openai_client.beta.threads.runs.stream(
                        thread_id=thread.id,
                        assistant_id=openai_assistant_id,
                        instructions="Please answer the users requests. Always answer in german!",
                ) as stream:
                    for event in stream:
                        match event.event:
                            case "thread.message.completed":
                                if event.data.content:
                                    content = event.data.content[0].text.value
                                    print(f"Answer: {content}")
                                    user_input_is_continue = input("Do you want to continue the chat?\n(y, n) ")
                                    time.sleep(1)
                                    if user_input_is_continue == 'y':
                                        user_input_question = input("What is your next question?\nQuestion: ")
                                        print("...thinking...")
                                    else:
                                        print("Okay. Thank you very much and come back soon. (y)")
                                        finished = True
                            case "thread.run.failed":
                                print(event)
                                print("run failed.")
                                finished = True
                                break
        except Exception as e:
            print(
                f"Sorry, something went wrong...:\n{e}")
            sys.exit()
