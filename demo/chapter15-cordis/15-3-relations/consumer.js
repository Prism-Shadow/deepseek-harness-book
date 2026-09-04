export const name = 'consumer'
export const inject = ['greeter']

export function apply(ctx) {
  console.log(ctx.greeter.greet('world'))
}
