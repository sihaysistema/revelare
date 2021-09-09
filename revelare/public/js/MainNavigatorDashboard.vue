<template>
  <div class="content-body">
    <div class="container-fluid">
      <div class="row">
        <DataCard />
      </div>
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