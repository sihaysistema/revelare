<template>
  <button v-on:click="count++">Button From Component 2 — {{ count }}</button>
</template>

<script>
export default {
  props: ["count"],
  data: function() {
    return {
      count: 0
    };
  }
};
</script>