export const name = 'waterfall-demo'

export function apply(ctx) {
  ctx.on('demo/transform', async (_input, next) => {
    console.log('A enter')
    const downstream = await next()
    console.log('A leave')
    return `A(${downstream})`
  })

  ctx.on('demo/transform', async (input, next) => {
    console.log('B enter')
    if (input.includes('blocked')) {
      console.log('B short-circuit')
      return 'blocked'
    }
    const downstream = await next()
    console.log('B leave')
    return `B(${downstream})`
  })

  void (async () => {
    console.log(await ctx.waterfall(
      'demo/transform',
      'hello',
      async () => {
        console.log('default')
        return 'hello'
      },
    ))

    console.log(await ctx.waterfall(
      'demo/transform',
      'blocked words',
      async () => {
        console.log('default')
        return 'blocked words'
      },
    ))
  })()
}
