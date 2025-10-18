# llmops

A simple llmops setup with a

    - chat front end
    - fast api backend
        - to handle chats
        - route to LLMs
    - guardrails server
    - arize logging enabled


## To run 
   
- Install Docker from [here](https://docs.docker.com/get-docker/)
- Run below commands

    ```
    git clone https://github.com/abhishek9sharma/llmops.git
    cd llmops.git
    make up_with_build
    ```
- Navigate to [http://localhost:8501/](http://localhost:8501/)