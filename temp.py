def main():
    try:
        with open("test_prompt.txt", "r", encoding="utf-8") as file:
            text = file.read()
    except FileNotFoundError:
        raise FileNotFoundError("test_prompt.txt not found.")

    input_data = OpenAIInput(text=text)
    request_temp = openai_request_process(input_data)

    print("===== FINAL PROMPT =====")
    print(request_temp.request)


if __name__ == "__main__":
    main()