from .prompt import prompt
from agent.profilebuilder.llm import llm, parser, prompt_template
def generate_weigths(content):
    # return "Hiis"
    
    chain = prompt_template | llm | parser
    res = chain.invoke({"prompt_text":prompt(content)})
    return res


def handle_engine_call(user,content):
    weights = generate_weigths(content)
    print(weights)