# from src.llm_generators.CodeGenerators import question_html_generator,server_js_generator,server_py_generator,solution_html_generator
# from src.semantic_search.semantic_search import SemanticSearch
# import asyncio
# from src.llm_generators.metadata_generator import generate_metadata_and_update



# # Test Implementation
# question = "A ball travels at a distance of 100 miles in 45 minutes along a straight path what is the speed of the ball "
# # question_html = asyncio.run(question_html_generator.arun(question))
# # print(question_html)
# # server_js = asyncio.run(server_js_generator.arun(question_html, f"Please analyze the problem, generate code using the same units as provided in the original question. Ensure all values are properly converted and consistent with the units from the question. Here is the question for reference: {question}"))
# # print(server_js)
# # server_py = asyncio.run(server_py_generator.arun(question_html, f"Please analyze the problem, generate code using the same units as provided in the original question. Ensure all values are properly converted and consistent with the units from the question. Here is the question for reference: {question}"))
# # print(server_py)
# # solution = asyncio.run(solution_html_generator.arun(question_html))
# # print(solution)


# print(asyncio.run(generate_metadata_and_update(question)))