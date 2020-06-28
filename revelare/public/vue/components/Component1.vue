<template>
  <button v-on:click="count++">Button From Component 1 — {{ count }}</button>
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

<style scoped>
.button {
  background-color: blue;
  border: none;
  color: white;
  padding: 15px 32px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  margin: 4px 2px;
  cursor: pointer;
}
</style>