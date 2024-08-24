from CustomAgents.TestAgent import TestAgent

learn = TestAgent()

text = """
        Large language models (LLMs) have been increasingly used to interact with exter-
        nal environments (e.g., games, compilers, APIs) as goal-driven agents. However,
        it remains challenging for these language agents to quickly and efficiently learn
        from trial-and-error as traditional reinforcement learning methods require exten-
        sive training samples and expensive model fine-tuning. We propose Reflexion , a
        novel framework to reinforce language agents not by updating weights, but in-
        stead through linguistic feedback. Concretely, Reflexion agents verbally reflect
        on task feedback signals, then maintain their own reflective text in an episodic
        memory buffer to induce better decision-making in subsequent trials. Reflexion is
        flexible enough to incorporate various types (scalar values or free-form language)
        and sources (external or internally simulated) of feedback signals, and obtains
        significant improvements over a baseline agent across diverse tasks (sequential
        decision-making, coding, language reasoning). For example, Reflexion achieves a
        91% pass@1 accuracy on the HumanEval coding benchmark, surpassing the previ-
        ous state-of-the-art GPT-4 that achieves 80%. We also conduct ablation and analysis
        studies using different feedback signals, feedback incorporation methods, and agent
        types, and provide insights into how they affect performance. We release all code,
        demos, and datasets at https://github.com/noahshinn024/reflexion . 
        1 Introduction
        Recent works such as ReAct [ 30], SayCan [ 1], Toolformer [ 22], HuggingGPT [ 23], generative
        agents [ 19], and WebGPT [ 17] have demonstrated the feasibility of autonomous decision-making
        agents that are built on top of a large language model (LLM) core. These methods use LLMs to
        generate text and �actions� that can be used in API calls and executed in an environment. Since
        they rely on massive models with an enormous number of parameters, such approaches have been
        so far limited to using in-context examples as a way of teaching the agents, since more traditional
        optimization schemes like reinforcement learning with gradient descent require substantial amounts
        of compute and time. 
        Preprint. Under review.arXiv:2303.11366v4  [cs. AI]  10 Oct 2023In this paper, we propose an alternative approach called Reflexion that uses verbal reinforcement
        to help agents learn from prior failings. Reflexion converts binary or scalar feedback from the
        environment into verbal feedback in the form of a textual summary, which is then added as additional
        context for the LLM agent in the next episode. This self-reflective feedback acts as a �semantic�
        gradient signal by providing the agent with a concrete direction to improve upon, helping it learn
        from prior mistakes to perform better on the task. This is akin to how humans iteratively learn to
        accomplish complex tasks in a few-shot manner � by reflecting on their previous failures in order to
        form an improved plan of attack for the next attempt. For example, in figure 1, a Reflexion agent
        learns to optimize its own behavior to solve decision-making, programming, and reasoning tasks
        through trial, error, and self-reflection. 
        Generating useful reflective feedback is challenging since it requires a good understanding of where
        the model made mistakes (i.e. the credit assignment problem [ 25]) as well as the ability to generate
        a summary containing actionable insights for improvement. We explore three ways for doing
        this � simple binary environment feedback, pre-defined heuristics for common failure cases, and
        self-evaluation such as binary classification using LLMs (decision-making) or self-written unit
        tests (programming). In all implementations, the evaluation signal is amplified to natural language
        experience summaries which can be stored in l
    """

result = learn.run(existing_knowledge="None", text_chunk=text)
# import os
# result = os.getenv('GROQ_API_KEY')
print(f"Final Results: {result}")

