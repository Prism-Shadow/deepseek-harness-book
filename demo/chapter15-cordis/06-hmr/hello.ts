import type { Context } from '@deepseek-ai/cordis'

export function apply(ctx: Context) {
  console.log('Hello, Cordis!')
  ctx.effect(() => {
    return () => console.log('hello 已卸载')
  })
}
