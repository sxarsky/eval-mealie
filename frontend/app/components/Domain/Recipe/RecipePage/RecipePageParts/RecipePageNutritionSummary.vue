<template>
  <v-card
    v-if="summary && summary.hasNutrition"
    class="mt-2"
    data-testid="recipe-nutrition-summary"
  >
    <v-card-title class="pt-2 pb-0">
      {{ $t("recipe.nutrition-per-serving") }}
    </v-card-title>
    <v-card-subtitle class="pb-1">
      <template v-if="summary.perServing">
        {{ $t("recipe.nutrition-per-serving-subtitle", { count: summary.servings }) }}
      </template>
      <template v-else>
        {{ $t("recipe.nutrition-per-serving-unavailable") }}
      </template>
    </v-card-subtitle>
    <v-divider class="mx-2 my-1" />
    <v-list
      density="compact"
      class="mt-0 pt-0"
    >
      <v-list-item
        v-for="(item, key) in renderedList"
        :key="key"
        style="min-height: 25px"
      >
        <v-list-item-title class="pl-2 d-flex">
          <div>{{ item.label }}</div>
          <div
            class="ml-auto mr-1"
            :data-testid="`nutrition-per-serving-${key}`"
          >
            {{ item.value }}
          </div>
          <div>{{ item.suffix }}</div>
        </v-list-item-title>
      </v-list-item>
    </v-list>
  </v-card>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";
import { useNutritionLabels } from "~/composables/recipes";
import type { NutritionLabelType } from "~/composables/recipes/use-recipe-nutrition";
import type { Nutrition, NutritionValues, RecipeNutritionSummary } from "~/lib/api/types/recipe";

interface Props {
  slug: string;
  servings?: number;
  nutrition?: Nutrition | null;
}
const props = withDefaults(defineProps<Props>(), {
  servings: 0,
  nutrition: null,
});

const api = useUserApi();
const { labels } = useNutritionLabels();
const summary = ref<RecipeNutritionSummary | null>(null);

async function loadSummary() {
  if (!props.slug) {
    summary.value = null;
    return;
  }

  const { data } = await api.recipes.getNutritionSummary(props.slug);
  summary.value = data;
}

// Reload when the recipe is saved with different servings or nutrition values
watch(() => [props.slug, props.servings, props.nutrition], loadSummary, { deep: true, immediate: true });

const renderedList = computed(() => {
  if (!summary.value) {
    return {};
  }

  const values: NutritionValues = summary.value.perServing ?? summary.value.total;
  return Object.entries(labels).reduce((items: NutritionLabelType, [key, label]) => {
    const value = values[key as keyof NutritionValues];
    if (value !== null && value !== undefined) {
      items[key] = {
        ...label,
        value: value.toString(),
      };
    }
    return items;
  }, {});
});
</script>
