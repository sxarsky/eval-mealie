import { useDark } from "@vueuse/core";

export default defineNuxtPlugin((nuxtApp) => {
  const applyThemeAttr = (dark: boolean) => {
    if (typeof document !== "undefined") {
      document.documentElement.setAttribute("data-theme", dark ? "dark" : "light");
    }
  };

  const isDark = useDark({
    onChanged: (v) => {
      console.log(`changing theme to ${v ? "dark" : "light"} using @vueuse/useDark`);
      const $vuetify = nuxtApp.vueApp.$nuxt.$vuetify;
      if ($vuetify)
        $vuetify.theme.toggle();
      applyThemeAttr(v);
    },
  });

  nuxtApp.hook("vuetify:ready", (vuetify) => {
    vuetify.theme.change(isDark.value ? "dark" : "light");
    applyThemeAttr(isDark.value);
  });

  return {
    provide: {},
  };
});
