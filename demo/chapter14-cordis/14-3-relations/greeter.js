import { Service } from '@deepseek-ai/cordis'

export class GreeterService extends Service {
  constructor(ctx) {
    super(ctx, 'greeter')
  }

  greet(who) {
    return `Hello, ${who}!`
  }
}

export const name = 'greeter'

export function apply(ctx) {
  ctx.plugin(GreeterService)
}
