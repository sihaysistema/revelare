<template>
  <div>
  <p>Random Number = {{ randomNumber }}</p>
  <button v-on:click="() => myFunction()">Click Me 2</button>
  </div>
</template>

<script>
export default {
  props: ["randomNumber"],
    data: {},
    methods: {
      myFunction: function (event) {
            var randomNumber = 0;
            this.randomNumber = Math.floor(Math.random()*100); //multiply to generate random number between 0, 100
            // console.log(randomNumber);
            return randomNumber;
        }
      }
    };
</script>

