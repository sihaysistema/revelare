<template>
  <div class="shs-container-fluid">
    <div class="row">
      <DataCard />
    </div>
  </div>
</template>

<script>
import DataCard from "./components/DataCard.vue";

export default {
  name: "MainNavigatorDashboard",
  components: {
    DataCard,
  },
};
</script>

<style>
</style>