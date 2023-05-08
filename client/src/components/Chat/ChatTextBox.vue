<template>
  <section class="input-container">
    <p>Note</p>
    <input class="input-text" placeholder="Start typing here..." />
    <p>Send</p>
  </section>
</template>

<script>
  export default {
    name: 'ChatTextBox',
    components: {

    },
    data() {
      return {
        
      }
    },
    methods: {

    },
    computed: {

    },
    created() {

    },
  }
</script>

<style lang="scss" scoped>
  @import '@/styles/variables';
  @import '@/styles/buttons';
  @import '@/styles/cards';
  @import '@/styles/mixins/utils';
  @import '@/styles/mixins/inputs';
  .input-container {
    display: flex;
    justify-content: space-between;
    margin: 0 1rem;
  }
  .input-text {
    width: 50vw;
    outline: none;
    border: 1px solid $very-light-gray;
    border-radius: 4px;
    box-shadow: 2px 2px 5px $very-light-gray;
  }
</style>