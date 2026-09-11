import { Service, type Context } from '@deepseek-ai/cordis'

declare module '@deepseek-ai/cordis' {
  interface Context {
    greeter: GreeterService
  }
  interface Events {
    'greeter/greeted'(who: string, message: string): void
  }
}

export class GreeterService extends Service {
  constructor(ctx: Context) {
    super(ctx, 'greeter')
  }

  greet(who: string) {
    const message = `Hello, ${who}!`
    this.ctx.emit('greeter/greeted', who, message)
    return message
  }
}

export function apply(ctx: Context) {
  ctx.plugin(GreeterService)
}
