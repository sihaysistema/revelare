<template>
  <button v-on:click="count++">SHS Vue Custom Button — {{ count }}</button>
</template>
<!-- Seems like a VUE component is an HTML page, trying a comment out-->
<script>
// Works great!
console.log("VUE Component Button Counter Loaded");
export default {
  props: ["count"],
  data: function() {
    return {
      count: 0
    };
  }
};
</script>