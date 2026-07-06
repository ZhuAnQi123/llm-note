[prompt template](https://docs.langchain.com/langsmith/create-a-prompt)
[promptingguide](https://www.promptingguide.ai/zh/introduction/tips)

example
```py
from langchain_core.prompts import PromptTemplate
template= PromptTemplate.from_template('Examplain {topic} to a {level} student.')
prmopt= template.format(topic="ai",level='beginner')
print(prompt)
```
