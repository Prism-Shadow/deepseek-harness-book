// tool-decide 插件，为 dsh 添加一个“随机做决定”工具。
import { defineTool } from '@deepseek-ai/dsh-tools'

// 插件名称可以自行指定，配置文件中的 name 字段需要与它一致。
export const name = 'tool-decide'
// 声明插件依赖工具注册表服务，dsh 会在 ctx.tools 可用后启动插件。
export const inject = ['tools']

export function apply(ctx) {
  ctx.tools.register(defineTool({
    // 提供给模型的工具名称。
    name: 'pick_one',
    // 提供给模型的工具说明，用于判断何时调用该工具。
    description: '当用户在几个选项里纠结、想随机选一个而不是要理性建议时，从给定的选项列表里随机选出一个。',
    // 模型调用工具时需要传入的参数。
    parameters: {
      options: {
        type: 'array',
        required: true,
        description: '待选项，至少两个。',
        items: { type: 'string' },
      },
    },
    // 定义返回给模型的结果结构。
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          picked: { type: 'string', required: true },
        },
      },
      render: (_args, value) => [{ type: 'text', text: `随机选中：${value.picked}` }],
    },
    // 工具的执行逻辑。
    execute(args) {
      const options = args.options
      if (!Array.isArray(options) || options.length < 2) {
        throw new Error('pick_one 至少需要两个选项')
      }
      const picked = options[Math.floor(Math.random() * options.length)]
      return Promise.resolve({ picked })
    },
  }))
}
