好的，这是您提供的框架技术文档的中文翻译：

---

# 文件和资源

## 附加文件

您可以使用路径 (Paths) 在对话中包含文件：

```python
from mcp_agent.core.prompt import Prompt
from pathlib import Path

plans = agent.send(
    Prompt.user(
        "总结这份 PDF 文档",
        Path("secret-plans.pdf")
    )
)
```

这适用于任何可以被模型进行词元化 (tokenized) 的 MIME 类型。

## MCP 资源

MCP 服务器资源可以通过以下方式便捷地包含在消息中：

```python
description = agent.with_resource(
    "这张图片里有什么？",
    "mcp_image_server", # MCP 服务器名称
    "resource://images/cat.png" # 资源 URI
)
```

## 提示文件 (Prompt Files)

提示文件可以包含资源：

agent_script.txt
```md
---USER
请从这个 CSS 文件中提取主要颜色：
---RESOURCE
index.css
```

它们既可以使用 `load_prompt_multipart` 函数加载，也可以通过内置的 `prompt-server` 提供。

# 定义代理 (Agents) 和工作流 (Workflows)

## 基本代理

定义一个代理非常简单：

```python
@fast.agent(
  instruction="给定一个对象，仅回复其大小的估算值。"
)
```

然后我们可以向该代理发送消息：

```python
async with fast.run() as agent:
  moon_size = await agent("月球")
  print(moon_size)
```

或者与代理开始一个交互式聊天：

```python
async with fast.run() as agent:
  await agent.interactive()
```

以下是完整的 `sizer.py` 代理应用程序，包含样板代码：

sizer.py
```python
import asyncio
from mcp_agent.core.fastagent import FastAgent

# 创建应用程序
fast = FastAgent("代理示例")

@fast.agent(
  instruction="给定一个对象，仅回复其大小的估算值。"
)
async def main():
  async with fast.run() as agent:
    await agent() # 如果没有提供消息，默认启动交互模式

if __name__ == "__main__":
    asyncio.run(main())
```

然后可以使用 `uv run sizer.py` 运行该代理。

使用 `--model` 开关指定模型 - 例如 `uv run sizer.py --model sonnet`。

## 工作流和 MCP 服务器

*要生成示例，请使用 `fast-agent quickstart workflow`。此示例可以通过 `uv run workflow/chaining.py` 运行。fast-agent 会先在当前目录查找配置文件，然后再递归检查父目录。*

代理可以被链接起来构建工作流，使用在 `fastagent.config.yaml` 文件中定义的 MCP 服务器：

fastagent.config.yaml
```yaml
# 一个名为 "fetch" 的 STDIO 服务器示例
mcp:
  servers:
    fetch:
      command: "uvx"
      args: ["mcp-server-fetch"]
```

social.py
```python
@fast.agent(
    "url_fetcher",
    "给定一个 URL，提供一个完整且全面的摘要",
    servers=["fetch"], # 在 fastagent.config.yaml 中定义的 MCP 服务器名称
)
@fast.agent(
    "social_media",
    """
    为任何给定的文本编写一个 280 个字符的社交媒体帖子。
    仅回复帖子内容，从不使用标签。
    """,
)
@fast.chain(
    name="post_writer",
    sequence=["url_fetcher", "social_media"],
)
async def main():
    async with fast.run() as agent:
        # 使用链式工作流
        await agent.post_writer("http://fast-agent.ai")
```

所有代理和工作流都响应 `.send("message")`。代理应用响应 `.interactive()` 来启动聊天会话。

保存为 `social.py` 后，我们现在可以使用以下命令从命令行运行此工作流：

```bash
uv run workflow/chaining.py --agent post_writer --message "<url>"
```

添加 `--quiet` 开关以禁用进度和消息显示，并仅返回最终响应——这对于简单的自动化很有用。

在此处阅读更多关于运行 **fast-agent** 代理的信息 [here](../running/)

## 工作流类型

**fast-agent** 内置支持 Anthropic 的 [构建有效代理 (Building Effective Agents)](https://www.anthropic.com/research/building-effective-agents) 论文中引用的模式。

### 链 (Chain)

`chain` 工作流提供了一种按顺序调用代理的声明式方法：

```python
@fast.chain(
  "post_writer",
   sequence=["url_fetcher","social_media"]
)

# 我们可以直接提示它：
async with fast.run() as agent:
  await agent.interactive(agent="post_writer")
```

这将启动一个交互式会话，为给定的 URL 生成一个简短的社交媒体帖子。如果提示一个*链*，它会返回到与链中最后一个代理的聊天。您可以通过键入 `@agent-name` 来切换代理。

链可以被包含在其他工作流中，或者包含其他工作流元素（包括其他链）。如果需要，您可以设置一个 `instruction` 来向其他工作流步骤描述其功能。

链在被 `router` 分派内容之前捕获内容，或在内容被用于下游工作流之前进行总结时也很有用。

### 人工输入 (Human Input)

代理可以请求人工输入以协助完成任务或获取额外的上下文：

```python
@fast.agent(
    instruction="一个协助完成基本任务的 AI 代理。在需要时请求人工输入。",
    human_input=True,
)

await agent("打印序列中的下一个数字")
```

在 `human_input.py` 示例中，代理将提示用户提供额外信息以完成任务。

### 并行 (Parallel)

并行工作流同时向多个代理发送相同的消息（`fan-out`），然后使用 `fan-in` 代理处理组合后的内容。

```python
@fast.agent("translate_fr", "将文本翻译成法语")
@fast.agent("translate_de", "将文本翻译成德语")
@fast.agent("translate_es", "将文本翻译成西班牙语")

@fast.parallel(
  name="translate",
  fan_out=["translate_fr","translate_de","translate_es"]
)

@fast.chain(
  "post_writer",
   sequence=["url_fetcher","social_media","translate"]
)
```

如果您没有指定 `fan-in` 代理，`parallel` 将原样返回组合的代理结果。

`parallel` 对于从不同的 LLM 汇集想法也很有用。

在其他工作流中使用 `parallel` 时，请指定一个 `instruction` 来描述其操作。

### 评估器-优化器 (Evaluator-Optimizer)

评估器-优化器结合了两个代理：一个用于生成内容（`generator`），另一个用于判断该内容并提供可操作的反馈（`evaluator`）。消息首先发送给生成器，然后这对代理在一个循环中运行，直到评估器对质量满意，或者达到最大优化次数。返回生成器的最终结果。

如果生成器的 `use_history` 设置为 off，则在请求改进时返回上一次迭代的结果——否则使用对话上下文。

```python
@fast.evaluator_optimizer(
  name="researcher"
  generator="web_searcher"
  evaluator="quality_assurance"
  min_rating="EXCELLENT"
  max_refinements=3
)

async with fast.run() as agent:
  await agent.researcher.send("生成一份关于如何制作完美浓缩咖啡的报告")
```

在工作流中使用时，它返回最后一个 `generator` 消息作为结果。

请参阅 `evaluator.py` 工作流示例，或 `fast-agent quickstart researcher` 获取更完整的示例。

### 路由器 (Router)

路由器使用 LLM 评估消息，并将其路由到最合适的代理。路由提示会根据代理指令和可用的服务器自动生成。

```python
@fast.router(
  name="route"
  agents=["agent1","agent2","agent3"]
)
```

注意 - 如果只向路由器提供一个代理，它会直接转发。

查看 `router.py` 工作流以获取示例。

### 编排器 (Orchestrator)

给定一个复杂的任务，编排器使用 LLM 生成一个计划，在可用的代理之间分配任务。规划和聚合提示由编排器生成，它能从使用更强大的模型中受益。计划可以在开始时一次性构建（`plantype="full"`），也可以迭代构建（`plantype="iterative"`）。

```python
@fast.orchestrator(
  name="orchestrate"
  agents=["task1","task2","task3"]
)
```

请参阅 `orchestrator.py` 或 `agent_build.py` 工作流示例。

## 代理和工作流参考

### 调用代理

所有定义都允许省略名称和指令参数以求简洁：

```python
@fast.agent("你是一个乐于助人的代理")          # 创建一个具有默认名称的代理。
@fast.agent("greeter","愉快地回应！")    # 创建一个名为 "greeter" 的代理。

moon_size = await agent("月球")             # 使用消息调用默认（第一个定义的）代理。

result = await agent.greeter("早上好！")   # 使用点符号按名称向代理发送消息。
result = await agent.greeter.send("你好！")     # 您可以显式调用 'send'。

agent["greeter"].send("晚上好！")          # 也支持通过字典访问代理。
```

在此处阅读更多关于提示代理的信息 [here](../prompting/)

### 定义代理

#### 基本代理

```python
@fast.agent(
  name="agent",                          # 代理名称
  instruction="你是一个乐于助人的代理", # 代理的基本指令
  servers=["filesystem"],                # 代理的 MCP 服务器列表
  model="o3-mini.high",                  # 为代理指定模型
  use_history=True,                      # 代理维护聊天历史
  request_params=RequestParams(temperature= 0.7), # LLM 的附加参数 (或 RequestParams())
  human_input=True,                      # 代理可以请求人工输入
)
```

#### 链 (Chain)

```python
@fast.chain(
  name="chain",                          # 链的名称
  sequence=["agent1", "agent2", ...],    # 按执行顺序列出的代理
  instruction="instruction",             # 为其他工作流描述此链的指令
  cumulative=False                       # 是否在链中累积消息
  continue_with_final=True,              # 提示后，与链末端的代理开始聊天
)
```

#### 并行 (Parallel)

```python
@fast.parallel(
  name="parallel",                       # 并行工作流的名称
  fan_out=["agent1", "agent2"],          # 并行运行的代理列表
  fan_in="aggregator",                   # 组合结果的代理名称（可选）
  instruction="instruction",             # 为其他工作流描述此并行的指令
  include_request=True,                  # 在 fan-in 消息中包含原始请求
)
```

#### 评估器-优化器 (Evaluator-Optimizer)

```python
@fast.evaluator_optimizer(
  name="researcher",                     # 工作流的名称
  generator="web_searcher",              # 内容生成器代理的名称
  evaluator="quality_assurance",         # 评估器代理的名称
  min_rating="GOOD",                     # 最低可接受质量 (EXCELLENT, GOOD, FAIR, POOR)
  max_refinements=3,                     # 最大优化迭代次数
)
```

#### 路由器 (Router)

```python
@fast.router(
  name="route",                          # 路由器的名称
  agents=["agent1", "agent2", "agent3"], # 路由器可以委托的代理名称列表
  instruction="routing instruction",     # 任何额外的路由指令
  servers=["filesystem"]                 # 路由代理的服务器列表
  model="o3-mini.high",                  # 指定路由模型
  use_history=False,                     # 路由器是否维护对话历史
  human_input=False,                     # 路由器是否可以请求人工输入
)
```

#### 编排器 (Orchestrator)

```python
@fast.orchestrator(
  name="orchestrator",                   # 编排器的名称
  instruction="instruction",             # 编排器的基本指令
  agents=["agent1", "agent2"],           # 此编排器可以使用的代理名称列表
  model="o3-mini.high",                  # 指定编排器规划模型
  use_history=False,                     # 编排器不维护聊天历史（无效果）。
  human_input=False,                     # 编排器是否可以请求人工输入
  plan_type="full",                      # 规划方法："full" 或 "iterative"
  max_iterations=5,                      # 最大完整计划尝试次数，或迭代次数
)
```

# 提示代理 (Prompting Agents)

**fast-agent** 提供了一个灵活的基于 MCP 的 API，用于向代理发送消息，并提供了处理文件、提示和资源的便捷方法。

在此处阅读更多关于 **fast-agent** 中 MCP 类型用法的信息 [here](../../mcp/types/)。

## 发送消息

向代理发送消息最简单的方法是 `send` 方法：

```python
response: str = await agent.send("你好吗？")
```

这将以字符串形式返回代理响应的文本，使其非常适合简单的交互。

您可以通过使用 `Prompt.user()` 方法构建消息来附加文件：

```python
from mcp_agent.core.prompt import Prompt
from pathlib import Path

plans: str = await agent.send(
    Prompt.user(
        "总结这份 PDF 文档",
        Path("secret-plans.pdf")
    )
)
```

`Prompt.user()` 会自动将内容转换为适当的 MCP 类型。例如，`image/png` 变成 `ImageContent`，`application/pdf` 变成 `EmbeddedResource`。

您也可以直接使用 MCP 类型 - 例如：

```python
from mcp.types import ImageContent, TextContent

mcp_text: TextContent = TextContent(type="text", text="分析这张图片。")
mcp_image: ImageContent = ImageContent(type="image",
                          mimeType="image/png",
                          data=base_64_encoded)

response: str  = await agent.send(
    Prompt.user(
        mcp_text,
        mcp_image
    )
)
```

> 注意：使用 `Prompt.assistant()` 来生成 `assistant` 角色的消息。

### 使用 `generate()` 和多部分内容

`generate()` 方法允许您访问代理的多模态内容或其工具调用 (Tool Calls)，以及发送对话对。

```python
from mcp_agent.core.prompt import Prompt
from mcp_agent.mcp.prompt_message_multipart import PromptMessageMultipart

message = Prompt.user("描述一张日落的图片")

response: PromptMessageMultipart = await agent.generate([message])

print(response.last_text())  # 主要文本响应
```

`send()` 和 `generate()` 之间的主要区别在于 `generate()` 返回一个 `PromptMessageMultipart` 对象，使您可以访问完整的响应结构：

- `last_text()`: 获取主要文本响应
- `first_text()`: 如果存在多个文本块，则获取第一个文本内容
- `all_text()`: 组合响应中的所有文本内容
- `content`: 直接访问内容部分的完整列表，包括图像和嵌入式资源 (EmbeddedResources)

这在处理多模态响应或工具输出时特别有用：

```python
# 生成可能包含多种内容类型的响应
response = await agent.generate([
    Prompt.user("分析这张图片", Path("chart.png"))
])

for content in response.content:
    if content.type == "text":
        print("文本响应:", content.text[:100], "...")
    elif content.type == "image":
        print("图片内容:", content.mimeType)
    elif content.type == "resource":
        print("资源:", content.resource.uri)
```

您还可以通过传递多条消息来使用 `generate()` 进行多轮对话：

```python
messages = [
    Prompt.user("法国的首都是哪里？"),
    Prompt.assistant("法国的首都是巴黎。"),
    Prompt.user("它的人口是多少？")
]

response = await agent.generate(messages)
```

`generate()` 方法为处理 LLM 返回的内容以及 MCP 工具、提示和资源调用提供了基础。

### 使用 `structured()` 获取类型化响应

当您需要代理以特定格式返回数据时，请使用 `structured()` 方法。这将代理的响应解析为一个 Pydantic 模型：

```python
from pydantic import BaseModel
from typing import List

# 定义您期望的响应结构
class CityInfo(BaseModel):
    name: str
    country: str
    population: int
    landmarks: List[str]

# 请求结构化信息
result, message = await agent.structured(
    [Prompt.user("告诉我关于巴黎的信息")],
    CityInfo
)

# 现在您拥有了强类型数据
if result:
    print(f"城市: {result.name}, 人口: {result.population:,}")
    for landmark in result.landmarks:
        print(f"- {landmark}")
```

`structured()` 方法返回一个包含以下内容的元组：

1.  解析后的 Pydantic 模型实例（如果解析失败则为 `None`）
2.  完整的 `PromptMessageMultipart` 响应

这种方法非常适合：

-   以一致的格式提取特定数据点
-   构建需要结构化输入/输出的代理工作流
-   将代理响应与类型化系统集成

始终检查第一个值是否为 `None`，以处理响应无法解析到您的模型中的情况：

```python
result, message = await agent.structured([Prompt.user("描述巴黎")], CityInfo)

if result is None:
    # 回退到文本响应
    print("无法解析结构化数据，原始响应：")
    print(message.last_text())
```

`structured()` 方法提供与 `generate()` 相同的请求参数选项。

注意

LLM 在生成结构化响应时会产生 JSON，这可能与工具调用冲突。使用 `chain` 来组合工具调用和结构化输出。

## MCP 提示

使用以下方式将来自 MCP 服务器的提示应用于代理：

```python
response: str = await agent.apply_prompt(
    "setup_sizing", # 提示名称
    arguments: {"units","metric"} # 提示参数
)
```

您可以列出并从附加的 MCP 服务器获取提示：

```python
from mcp.types import GetPromptResult, PromptMessage

prompt: GetPromptResult = await agent.get_prompt("setup_sizing")
first_message: PromptMessage = prompt[0] # GetPromptResult 是一个 PromptMessage 列表
```

并使用以下方式将原生的 MCP `PromptMessage` 发送给代理：

```python
response: str = agent.send(first_message)
```

> 如果对话中的最后一条消息来自 `assistant`，则将其作为响应返回。

## MCP 资源

`Prompt.user` 也适用于 MCP 资源：

```python
from mcp.types import ReadResourceResult

resource: ReadResourceResult = agent.get_resource(
    "resource://images/cat.png", "mcp_server_name"
)
response: str = agent.send(
    Prompt.user("这张图片里有什么？", resource)
)
```

或者，使用 *with_resource* 便捷方法：

```python
response: str = agent.with_resource(
    "这张图片里有什么？",
    "resource://images/cat.png"
    "mcp_server_name",
)
```

## 提示文件

长提示可以存储在文本文件中，并使用 `load_prompt` 工具加载：

```python
from mcp_agent.mcp.prompts import load_prompt
from mcp.types import PromptMessage

prompt: List[PromptMessage] = load_prompt(Path("two_cities.txt"))
result: str = await agent.send(prompt[0])
```

two_cities.txt
```markdown
### The Period (时代背景)

It was the best of times, it was the worst of times, it was the age of
wisdom, it was the age of foolishness, it was the epoch of belief, it was
the epoch of incredulity, ... (那是最美好的时代，那是最糟糕的时代，那是智慧的年头，那是愚昧的年头，那是信仰的纪元，那是怀疑的纪元，……)
```

提示文件可以包含对话，以辅助上下文学习或允许您使用 Playback LLM 重放对话：

sizing_conversation.txt
```markdown
---USER
月球
---ASSISTANT
object: MOON
size: 3,474.8
units: KM
---USER
地球
---ASSISTANT
object: EARTH
size: 12,742
units: KM
---USER
老虎有多大？
---ASSISTANT
object: TIGER
size: 1.2
units: M
```

可以使用 `generate()` 方法应用多条消息（对话）：

```python
from mcp_agent.mcp.prompts import load_prompt
from mcp.types import PromptMessage

prompt: List[PromptMessage] = load_prompt(Path("sizing_conversation.txt"))
result: PromptMessageMultipart = await agent.generate(prompt)
```

对话文件也可以用于包含资源：

prompt_secret_plans.txt
```markdown
---USER
请审阅以下文件：
---RESOURCE
secret_plan.pdf
---RESOURCE
repomix.xml
---ASSISTANT
感谢您提供的这些文件，PDF 包含了秘密计划，并且附加了一些源代码以实现这些计划。我还能提供进一步的帮助吗？
```

通常情况下，使用 `load_prompt_multipart` 更好（但不是必须的）：

```python
from mcp_agent.mcp.prompts import load_prompt_multipart
from mcp_agent.mcp.PromptMessageMultipart # 应该是 PromptMessageMultipart

prompt: List[PromptMessageMultipart] = load_prompt_multipart(Path("prompt_secret_plans.txt"))
result: PromptMessageMultipart = await agent.generate(prompt)
```

文件格式 / MCP 序列化

如果文件类型是 `json`，则消息使用 MCP 提示模式格式进行反序列化。`load_prompt`、`load_prompt_multipart` 和 `prompt-server` 将直接加载文本或 JSON 格式。请参阅[历史记录保存](../../models/#history-saving)以了解如何将对话保存到文件以进行编辑或回放。

### 使用 `prompt-server`

提示文件也可以使用内置的 `prompt-server` 提供。`prompt-server` 命令随 `fast-agent` 一起安装，使其设置和使用非常方便：

fastagent.config.yaml
```yaml
mcp:
  servers:
    prompts:
      command: "prompt-server"
      args: ["prompt_secret_plans.txt"]
```

这将配置一个 MCP 服务器，该服务器将提供一个 `prompt_secret_plans` MCP 提示，以及 `secret_plan.pdf` 和 `repomix.xml` 作为 MCP 资源。

如果模板文件中提供了参数，`prompt-server` 也会处理这些参数。

prompt_with_args.txt
```markdown
---USER
你好 {{assistant_name}}，你好吗？
---ASSISTANT
很高兴认识你 {{user_name}}，我能帮你什么忙吗？
```

# 部署和运行

**fast-agent** 提供灵活的部署选项，以满足各种用例，从交互式开发到生产服务器部署。

## 交互模式

以交互方式运行 **fast-agent** 程序，用于开发、调试或直接用户交互。

agent.py
```python
import asyncio
from mcp_agent.core.fastagent import FastAgent

fast = FastAgent("我的交互式代理")

@fast.agent(instruction="你是一个乐于助人的助手")
async def main():
    async with fast.run() as agent:
        # 启动交互式提示
        await agent()

if __name__ == "__main__":
    asyncio.run(main())
```

当使用 `uv run agent.py` 启动时，这将开始一个交互式提示，您可以直接与配置的代理聊天、应用提示、保存历史记录等。

## 命令行执行

**fast-agent** 支持命令行参数，以使用特定消息运行代理和工作流。

```bash
# 向特定代理发送消息
uv run agent.py --agent default --message "分析这个数据集"

# 覆盖默认模型
uv run agent.py --model gpt-4o --agent default --message "复杂问题"

# 以最小输出运行
uv run agent.py --quiet --agent default --message "后台任务"
```

这非常适合脚本编写、自动化或一次性查询。

`--quiet` 标志会关闭进度、聊天和工具显示。

## MCP 服务器部署

任何 **fast-agent** 应用程序都可以通过一个简单的命令行开关部署为 MCP（消息控制协议）服务器。

### 启动 MCP 服务器

```bash
# 作为 SSE 服务器启动 (HTTP)
uv run agent.py --server --transport sse --port 8080

# 作为 stdio 服务器启动 (用于管道传输到其他进程)
uv run agent.py --server --transport stdio
```

每个代理都公开一个用于向代理发送消息的 MCP 工具，以及一个返回对话历史的提示。

这使得通过 MCP 提示实现跨代理状态转移成为可能。

MCP 服务器也可以通过编程方式启动。

### 编程式服务器启动

```python
import asyncio
from mcp_agent.core.fastagent import FastAgent

fast = FastAgent("服务器代理")

@fast.agent(instruction="你是一个 API 代理")
async def main():
    # 以编程方式启动服务器
    await fast.start_server(
        transport="sse",
        host="0.0.0.0",
        port=8080,
        server_name="API-Agent-Server",
        server_description="为我的代理提供 API 访问"
    )

if __name__ == "__main__":
    asyncio.run(main())
```

## Python 程序集成

将 **fast-agent** 嵌入到现有的 Python 应用程序中以添加 MCP 代理功能。

```python
import asyncio
from mcp_agent.core.fastagent import FastAgent

fast = FastAgent("嵌入式代理")

@fast.agent(instruction="你是一个数据分析助手")
async def analyze_data(data):
    async with fast.run() as agent:
        result = await agent.send(f"分析这些数据：{data}")
        return result

# 在您的应用程序中使用
async def main():
    user_data = get_user_data()
    analysis = await analyze_data(user_data)
    display_results(analysis)

if __name__ == "__main__":
    asyncio.run(main())
```

# 模型特性与历史记录保存

**fast-agent** 中的模型通过一个模型字符串指定，格式为 `provider.model_name.<reasoning_effort>`

### 优先级

fast-agent 中的模型规范遵循以下优先级顺序（从高到低）：

1.  在代理装饰器中显式设置
2.  使用 `--model` 标志的命令行参数
3.  `fastagent.config.yaml` 中的默认模型

### 格式

模型字符串遵循此格式：`provider.model_name.reasoning_effort`

-   **provider**: LLM 提供商 (例如, `anthropic`, `openai`, `deepseek`, `generic`,`openrouter`, `tensorzero`)
-   **model_name**: API 调用中使用的特定模型
-   **reasoning_effort** (可选): 控制支持模型的推理强度

示例:

-   `anthropic.claude-3-7-sonnet-latest`
-   `openai.gpt-4o`
-   `openai.o3-mini.high`
-   `generic.llama3.2:latest`
-   `openrouter.google/gemini-2.5-pro-exp-03-25:free`
-   `tensorzero.my_tensorzero_function`

#### 推理强度 (Reasoning Effort)

对于支持它的模型（`o1`、`o1-preview` 和 `o3-mini`），您可以指定 **`high`**、**`medium`** 或 **`low`** 的推理强度 - 例如 `openai.o3-mini.high`。如果未指定，则默认为 **`medium`**。

#### 别名 (Aliases)

为方便起见，流行的模型设置了别名，例如 `gpt-4o` 或 `sonnet`。这些记录在 [LLM 提供商 (LLM Providers)](llm_providers/) 页面上。

### 默认配置

您可以在 `fastagent.config.yaml` 中为您的应用程序设置默认模型：

```yaml
default_model: "openai.gpt-4o" # 所有代理的默认模型
```

### 历史记录保存

您可以通过发送 `***SAVE_HISTORY <filename>` 消息将对话历史保存到文件。然后可以使用 `prompt-server` 对其进行审阅、编辑、加载或提供服务，或使用 `playback` 模型进行重放。

文件格式 / MCP 序列化

如果文件类型是 `json`，则消息使用 MCP 提示模式进行序列化/反序列化。`load_prompt`、`load_prompt_multipart` 和 `prompt-server` 将直接加载文本或 JSON 格式。

这在开发应用程序时很有帮助，可以：

-   保存对话以供编辑
-   设置上下文学习
-   使用 [Playback 模型](internal_models/#playback) 生成真实的测试场景以测试边缘条件等。

**fast-agent** 自带两个内部模型以辅助开发和测试：`passthrough` 和 `playback`。

## 透传 (Passthrough)

默认情况下，`passthrough` 模型会回显发送给它的消息。

### 固定响应

通过发送 `***FIXED_RESPONSE <message>` 消息，模型将对任何请求返回 `<message>`。

### 工具调用

通过发送 `***CALL_TOOL <tool_name> [<json>]` 消息，模型将调用指定的 MCP 工具，并返回包含结果的字符串。

## 回放 (Playback)

`playback` 模型会重放发送给它的第一个对话。典型用法可能如下所示：

playback.txt
```markdown
---USER
早上好！
---ASSISTANT
你好
---USER
生成一些 JSON
---ASSISTANT
{
   "city": "伦敦",
   "temperature": 72
}
```

然后可以与 `prompt-server` 一起使用，您可以通过编程方式使用 `apply_prompt` 或在交互式 shell 中使用 `/prompts` 命令将 MCP 提示应用于代理。

或者，您可以使用 `load_message_multipart` 加载文件。

JSON 内容可以转换为结构化输出：

```python
@fast.agent(name="playback",model="playback")

...

playback_messages: List[PromptMessageMultipart] = load_message_multipart(Path("playback.txt"))
# 设置对话
assert ("HISTORY LOADED") == agent.playback.generate(playback_messages)

response: str = agent.playback.send("早上好！") # 返回 你好
temperature, _ = agent.playback.structured("生成一些 JSON")
```

当 `playback` 耗尽消息时，它会返回 `MESSAGES EXHAUSTED (list size [a]) ([b] overage)`。

列表大小是最初加载的总消息数，超额是耗尽后发出的请求数。

对于每个模型提供商，您可以通过环境变量或在 `fastagent.config.yaml` 文件中配置参数。

请务必运行 `fast-agent check` 来排查 API 密钥问题：

## 通用配置格式

在您的 `fastagent.config.yaml` 中：

```yaml
<provider>:
  api_key: "your_api_key" # 通过 API_KEY 环境变量覆盖
  base_url: "https://api.example.com" # API 调用的基础 URL
```

## Anthropic

Anthropic 模型支持文本、视觉和 PDF 内容。

**YAML 配置：**

```yaml
anthropic:
  api_key: "your_anthropic_key" # 必需
  base_url: "https://api.anthropic.com/v1" # 默认，仅在需要时包含
```

**环境变量：**

-   `ANTHROPIC_API_KEY`: 您的 Anthropic API 密钥
-   `ANTHROPIC_BASE_URL`: 覆盖 API 端点

**模型名称别名：**

| 模型别名 | 映射到                         | 模型别名  | 映射到                         |
| :------- | :----------------------------- | :-------- | :----------------------------- |
| `claude` | `claude-3-7-sonnet-latest`     | `haiku`   | `claude-3-5-haiku-latest`      |
| `sonnet` | `claude-3-7-sonnet-latest`     | `haiku3`  | `claude-3-haiku-20240307`      |
| `sonnet35`| `claude-3-5-sonnet-latest`     | `haiku35` | `claude-3-5-haiku-latest`      |
| `sonnet37`| `claude-3-7-sonnet-latest`     | `opus`    | `claude-3-opus-latest`         |
| `opus3`  | `claude-3-opus-latest`         |           |                                |

## OpenAI

**fast-agent** 支持 OpenAI `gpt-4.1`、`gpt-4.1-mini`、`o1-preview`、`o1` 和 `o3-mini` 模型。使用 `openai.<model_name>` 支持任意模型名称。支持的模态取决于模型，请查看 [OpenAI 模型页面](https://platform.openai.com/docs/models) 获取最新信息。

结构化输出使用 OpenAI API 结构化输出功能。

**fast-agent** 的未来版本将具有增强的模型能力处理。

**YAML 配置：**

```yaml
openai:
  api_key: "your_openai_key" # 默认
  base_url: "https://api.openai.com/v1" # 默认，仅在需要时包含
```

**环境变量：**

-   `OPENAI_API_KEY`: 您的 OpenAI API 密钥
-   `OPENAI_BASE_URL`: 覆盖 API 端点

**模型名称别名：**

| 模型别名    | 映射到         | 模型别名       | 映射到         |
| :---------- | :------------- | :------------- | :------------- |
| `gpt-4o`    | `gpt-4o`       | `gpt-4.1`      | `gpt-4.1`      |
| `gpt-4o-mini`| `gpt-4o-mini`  | `gpt-4.1-mini` | `gpt-4.1-mini` |
| `o1`        | `o1`           | `gpt-4.1-nano` | `gpt-4.1-nano` |
| `o1-mini`   | `o1-mini`      | `o1-preview`   | `o1-preview`   |
| `o3-mini`   | `o3-mini`      |                |                |

## DeepSeek

支持 DeepSeek v3 进行文本和工具调用。

**YAML 配置：**

```yaml
deepseek:
  api_key: "your_deepseek_key"
  base_url: "https://api.deepseek.com/v1"
```

**环境变量：**

-   `DEEPSEEK_API_KEY`: 您的 DeepSeek API 密钥
-   `DEEPSEEK_BASE_URL`: 覆盖 API 端点

**模型名称别名：**

| 模型别名   | 映射到          |
| :--------- | :-------------- |
| `deepseek` | `deepseek-chat` |
| `deepseek3`| `deepseek-chat` |

## Google

目前通过 OpenAI 兼容性端点支持 Google，计划很快提供第一方支持。

**YAML 配置：**

```yaml
google:
  api_key: "your_google_key"
  base_url: "https://generativelanguage.googleapis.com/v1beta/openai"
```

**环境变量：**

-   `GOOGLE_API_KEY`: 您的 Google API 密钥

**模型名称别名：**

*未映射*

## 通用 OpenAI / Ollama

以 `generic` 为前缀的模型将使用通用的 OpenAI 端点，默认配置为与 Ollama 的 [OpenAI 兼容性](https://github.com/ollama/ollama/blob/main/docs/openai.md) 一起工作。

这意味着要运行 Llama 3.2 最新版，您可以为模型字符串指定 `generic.llama3.2:latest`，并且不需要进一步的配置。

警告

通用提供商已针对 `qwen2.5:latest` 和 `llama3.2:latest` 的工具调用和结构化生成进行了测试。其他模型和配置可能无法按预期工作 - 请自行承担风险。

**YAML 配置：**

```yaml
generic:
  api_key: "ollama" # Ollama 的默认值，根据需要更改
  base_url: "http://localhost:11434/v1" # Ollama 的默认值
```

**环境变量：**

-   `GENERIC_API_KEY`: 您的 API 密钥 (Ollama 默认为 `ollama`)
-   `GENERIC_BASE_URL`: 覆盖 API 端点

**与其他 OpenAI API 兼容提供商一起使用：** 通过配置 `base_url` 和适当的 `api_key`，您可以连接到任何与 OpenAI API 兼容的提供商。

## OpenRouter

使用 [OpenRouter](https://openrouter.ai/) 聚合服务。模型通过与 OpenAI 兼容的 API 访问。支持的模态取决于 OpenRouter 上选择的特定模型。

模型*必须*使用 `openrouter.` 前缀，后跟来自 OpenRouter 的完整模型路径（例如，`openrouter.google/gemini-flash-1.5`）。

警告

OpenRouter 和 Google Gemini 模型之间存在一个问题，导致大型工具调用块内容被删除。

**YAML 配置：**

```yaml
openrouter:
  api_key: "your_openrouter_key" # 必需
  base_url: "https://openrouter.ai/api/v1" # 默认，仅在需要覆盖时包含
```

**环境变量：**

-   `OPENROUTER_API_KEY`: 您的 OpenRouter API 密钥
-   `OPENROUTER_BASE_URL`: 覆盖 API 端点

**模型名称别名：**

OpenRouter 不像 Anthropic 或 OpenAI 那样使用别名。您必须始终使用 `openrouter.provider/model-name` 格式。

## TensorZero

[TensorZero](https://tensorzero.com/) 是一个用于构建生产级 LLM 应用程序的开源框架。它统一了 LLM 网关、可观察性、优化、评估和实验。

目前，您必须将 TensorZero 网关作为单独的服务运行（例如使用 Docker）。有关如何部署 TensorZero 网关的更多信息，请参阅 [TensorZero 快速入门](https://tensorzero.com/docs/quickstart) 和 [TensorZero 网关部署指南](https://www.tensorzero.com/docs/gateway/deployment/)。

您可以通过在 `fast-agent` 中为您在 TensorZero 配置 (`tensorzero.toml`) 中定义的函数名称添加 `tensorzero.` 前缀来调用该函数（例如 `tensorzero.my_function_name`）。

**YAML 配置：**

```yaml
tensorzero:
  base_url: "http://localhost:3000" # 可选，仅在需要覆盖时包含
```

**环境变量：**

无（模型提供商凭据应提供给 TensorZero 网关）

# MCP 服务器

MCP 服务器在 `fastagent.config.yaml` 文件中配置。密钥可以保存在 `fastagent.secrets.yaml` 中，该文件遵循相同的格式（**fast-agent** 会合并这两个文件的内容）。

## 添加 STDIO 服务器

以下显示了配置名为 `server_one` 的 MCP 服务器的示例。

fastagent.config.yaml
```yaml
mcp:
# 在代理服务器数组中使用的名称
  server_one:
    # 要运行的命令
    command: "npx"
    # 命令的参数列表
    args: ["@modelcontextprotocol/server-brave-search"]
    # 环境变量的键/值对
    env:
      BRAVE_API_KEY: your_key
      KEY: value
  server_two:
    # 以此类推 ...
```

然后，此 MCP 服务器可以与代理一起使用，如下所示：

```python
@fast.agent(name="Search", servers=["server_one"])
```

## 添加 SSE 服务器

要使用 SSE 服务器，请指定 `sse` 传输并指定端点 URL 和标头：

fastagent.config.yaml
```yaml
mcp:
# 在代理服务器数组中使用的名称
  server_two:
    transport: "sse"
    # 连接的 url
    url: "http://localhost:8000/sse"
    # 用于 sse 会话的超时秒数（可选）
    read_transport_sse_timeout_seconds: 300
    # 连接的请求标头
    headers:
          Authorization: "Bearer <secret>"
```

## 根 (Roots)

**fast-agent** 支持 MCP 根。根是按服务器配置的：

fastagent.config.yaml
```yaml
mcp:
  server_three:
    transport: "sse"
    url: "http://localhost:8000/sse"
    roots:
       uri: "file://...."
       name: Optional Name # 可选名称
       server_uri_alias: # optional # 可选
```

根据 [MCP 规范](https://github.com/modelcontextprotocol/specification/blob/41749db0c4c95b97b99dc056a403cf86e7f3bc76/schema/2025-03-26/schema.ts#L1185-L1191)，根必须是以 `file://` 开头的有效 URI。

如果提供了 server_uri_alias，**fast-agent** 会将其呈现给 MCP 服务器。这允许您向 MCP 服务器呈现一致的接口。这种用法的一个示例是将本地目录挂载到 docker 卷，并将其呈现为 `/mnt/data` 给 MCP 服务器以保持一致性。

数据分析示例 (`fast-agent quickstart data-analysis`) 有一个 MCP 根的工作示例。

## 采样 (Sampling)

通过为 MCP 服务器指定采样模型来配置采样。

fastagent.config.yaml
```yaml
mcp:
  server_four:
    transport: "sse"
    url: "http://localhost:8000/sse"
    sampling:
      model: "provider.model.<reasoning_effort>"
```

在此处阅读更多关于模型字符串和设置的信息 [here](../models/)。采样请求支持视觉 - 尝试 [`@llmindset/mcp-webcam`](https://github.com/evalstate/mcp-webcam) 以获取示例。

以下是一些使用模型上下文协议 (MCP) 进行开发的推荐资源：

| 资源                                                                 | 描述                                                                 |
| :------------------------------------------------------------------- | :------------------------------------------------------------------- |
| [使用文件和资源 (Working with Files and Resources)](https://llmindset.co.uk/posts/2025/01/mcp-files-resources-part1/) | 探讨 MCP 服务器和主机开发人员共享丰富内容的选项                         |
| [PulseMCP 社区](https://www.pulsemcp.com/)                             | 一个以社区为中心的网站，提供 MCP 服务器的新闻、最新目录和用例              |
| [基础记忆 (Basic Memory)](https://memory.basicmachines.co/docs/introduction) | 高质量、基于 markdown 的 LLM 知识库 - 也适用于代理开发               |
| [Repomix](https://repomix.com/guide/)                                | 从文件夹或直接从 GitHub 创建 LLM 友好的文件。作为 MCP 服务器包含 - 或在创建代理输入之前从脚本运行 |
| [PromptMesh 工具](https://promptmesh.io/)                            | 处于 MCP 开发前沿的高质量工具和库                                      |
| [mcp-hfspace](https://github.com/evalstate/mcp-hfspace)              | 无缝连接数百个开源模型，包括图像和音频生成器等                           |
| [wong2 mcp-cli](https://github.com/wong2/mcp-cli)                    | 一个快速、轻量级的命令行替代官方 MCP Inspector 的工具                  |

# 快速入门：使用 MCP 进行状态转移

在这个快速入门中，我们将演示 **fast-agent** 如何使用 MCP 提示在两个代理之间转移状态。

首先，我们将 `agent_one` 作为 MCP 服务器启动，并使用 MCP Inspector 工具向其发送一些消息。

接下来，我们将运行 `agent_two` 并使用 MCP 提示从 `agent_one` 转移对话。

最后，我们将了解 **fast-agent** 的 `prompt-server` 以及它如何帮助构建代理应用程序。

您需要 API 密钥才能连接到[支持的模型](../../models/llm_providers/)，或者使用 Ollama 的 [OpenAI 兼容性](https://github.com/ollama/ollama/blob/main/docs/openai.md) 模式来使用本地模型。

快速入门还使用了 MCP Inspector - 请在此处查看[安装说明](https://modelcontextprotocol.io/docs/tools/inspector)。

## 步骤 1：设置 **fast-agent**

```bash
# 创建并切换到一个新目录
mkdir fast-agent && cd fast-agent

# 创建并激活一个 python 环境
uv venv
source .venv/bin/activate

# 设置 fast-agent
uv pip install fast-agent-mcp

# 创建状态转移示例
fast-agent quickstart state-transfer
```

```pwsh
# 创建并切换到一个新目录
md fast-agent; cd fast-agent # PowerShell 中 md 创建目录后不会自动切换，所以用分号连接命令

# 创建并激活一个 python 环境
uv venv
.venv\Scripts\activate

# 设置 fast-agent
uv pip install fast-agent-mcp

# 创建状态转移示例
fast-agent quickstart state-transfer
```

切换到 state-transfer 目录 (`cd state-transfer`)，将 `fastagent.secrets.yaml.example` 重命名为 `fastagent.secrets.yaml` 并输入您希望使用的提供商的 API 密钥。

提供的 `fastagent.config.yaml` 文件包含 `gpt-4o` 的默认值 - 如果您愿意，可以编辑它。

最后，运行 `uv run agent_one.py` 并发送一条测试消息以确保一切正常。输入 `stop` 返回命令行。

## 步骤 2：将 **agent one** 作为 MCP 服务器运行

要将 `"agent_one"` 作为 MCP 服务器启动，请运行以下命令：

```bash
# 将 agent_one 作为 MCP 服务器启动：
uv run agent_one.py --server --transport sse --port 8001
```

```pwsh
# 将 agent_one 作为 MCP 服务器启动：
uv run agent_one.py --server --transport sse --port 8001
```

代理现在可作为 MCP 服务器使用。

注意

此示例在端口 8001 上启动服务器。要使用不同的端口，请更新 `fastagent.config.yaml` 和 MCP Inspector 中的 URL。

## 步骤 3：连接并与 **agent one** 聊天

从另一个命令行运行模型上下文协议 (Model Context Protocol) 检查器以连接到代理：

```bash
# 运行 MCP 检查器
npx @modelcontextprotocol/inspector
```

```pwsh
# 运行 MCP 检查器
npx @modelcontextprotocol/inspector
```

选择 SSE 传输类型和 URL `http://localhost:8001/sse`。单击 `connect` 按钮后，您可以从 `tools` 选项卡与代理交互。使用 `agent_one_send` 工具向代理发送聊天消息并查看其响应。

可以从 `prompts` 选项卡查看对话历史。使用 `agent_one_history` 提示查看它。

断开 Inspector 的连接，然后在命令窗口中按 `ctrl+c` 停止进程。

## 步骤 4：将对话转移到 **agent two**

我们现在可以将对话转移并继续与 `agent_two` 进行。

使用以下命令运行 `agent_two`：

```bash
# 启动 agent_two： (原文没有 --server，保持一致)
uv run agent_two.py
```

```pwsh
# 启动 agent_two： (原文没有 --server，保持一致)
uv run agent_two.py
```

启动后，键入 `'/prompts'` 查看可用的提示。选择 `1` 将来自 `agent_one` 的提示应用于 `agent_two`，从而转移对话上下文。

您现在可以继续与 `agent_two` 聊天（可能使用不同的模型、MCP 工具或工作流组件）。

### 配置概述

**fast-agent** 使用以下配置文件连接到 `agent_one` MCP 服务器：

fastagent.config.yaml
```yaml
# MCP 服务器
mcp:
    servers:
        agent_one:
          transport: sse
          url: http://localhost:8001
```

然后 `agent_two` 在其定义中引用该服务器：

```python
# 定义代理
@fast.agent(name="agent_two",
            instruction="你是一个乐于助人的 AI 代理",
            servers=["agent_one"])

async def main():
    # 使用 --model 命令行开关或代理参数来更改模型
    async with fast.run() as agent:
        await agent.interactive()
```

## 步骤 5：保存/重新加载对话

**fast-agent** 使您能够保存和重新加载对话。

在 `agent_two` 聊天中输入 `***SAVE_HISTORY history.json` 以 MCP `GetPromptResult` 格式保存对话历史。

您也可以将其保存为文本格式以便于编辑。

通过使用提供的 MCP `prompt-server`，我们可以重新加载保存的提示并将其应用于我们的代理。将以下内容添加到您的 `fastagent.config.yaml` 文件中：

```yaml
# MCP 服务器
mcp:
    servers:
        prompts:
            command: prompt-server
            args: ["history.json"]
        agent_one:
          transport: sse
          url: http://localhost:8001
```

然后更新 `agent_two.py` 以使用新的服务器：

```python
# 定义代理
@fast.agent(name="agent_two",
            instruction="你是一个乐于助人的 AI 代理",
            servers=["prompts"]) # 更新为使用 "prompts" 服务器
```

运行 `uv run agent_two.py`，然后您可以使用 `/prompts` 命令加载较早的对话历史，并从上次中断的地方继续。

请注意，提示可以包含任何 MCP 内容类型，因此可以包含图像、音频和其他嵌入式资源。

您还可以使用 [Playback LLM](../../models/internal_models/) 来重放较早的聊天（对测试很有用！）

# 与 MCP 类型集成

## MCP 类型兼容性

FastAgent 旨在与 MCP SDK 类型系统无缝集成：

与助手的对话基于 `PromptMessageMultipart` - 这是 mcp `PromptMessage` 类型的扩展，支持多个内容部分。此类型预计将在 MCP 的未来版本中成为原生类型：https://github.com/modelcontextprotocol/specification/pull/198

## 消息历史转移

FastAgent 使在代理之间转移对话历史变得容易：

history_transfer.py
```python
@fast.agent(name="haiku", model="haiku")
@fast.agent(name="openai", model="o3-mini.medium")

async def main() -> None:
    async with fast.run() as agent:
        # 与 "haiku" 开始一个交互式会话
        await agent.prompt(agent_name="haiku")
        # 将消息历史转移到 "openai" (使用 PromptMessageMultipart)
        await agent.openai.generate(agent.haiku.message_history)
        # 继续对话
        await agent.prompt(agent_name="openai")
```

---