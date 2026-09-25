import { Container, getContainer } from "@cloudflare/containers";

export class QMBot extends Container {
  defaultPort = 10000;
  sleepAfter = "1h";

  constructor(ctx, env) {
    super(ctx, env);
    this.envVars = {
      BOT_TOKEN: env.BOT_TOKEN,
      ADMIN_ID: env.ADMIN_ID,
    };
  }
}

export default {
  async fetch(request, env) {
    return getContainer(env.QM_BOT).fetch(request);
  },
  async scheduled(_event, env) {
    await getContainer(env.QM_BOT).fetch(new Request("http://container/"));
  },
};
