import type { Context } from '@deepseek-ai/cordis'
import type {} from './greeter.ts'

export const inject = ['greeter']

export function apply(ctx: Context) {
  ctx.on('greeter/greeted', (who, message) => {
    console.log(`[事件] 问候 ${who}：${message}`)
  })

  const message = ctx.greeter.greet('world')
  console.log(`[返回值] ${message}`)
}
