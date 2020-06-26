<template>
  <button v-on:click="count++">SHS Vue Custom Button — {{ count }}</button>
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