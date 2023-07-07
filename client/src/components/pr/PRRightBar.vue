<template>
  <div class="right-bar">
    <div>
      <h3>Title</h3>
    </div>
    <div class="display-flex">
      <div @click="changeResource('Source')">Source</div>
      <div @click="changeResource('Data')">Data</div>
      <div @click="changeResource('Chat')">Chat</div>
    </div>
    <div>
      {{ selectedResource }} here
    </div>
  </div>
</template>
<script>
export default {
  name: 'PRRightBar',
  components: {

  },
  data() {
    return {
      selectedResource: 'Data',
    }
  },
  watch: {

  },
  created() {

  },
  methods: {
    changeResource(resource) {
      this.selectedResource = resource
    }
  },
  computed: {
    
  }
}
</script>
<style scoped>
  .right-bar {

  }
  .display-flex {
    display: flex;
  }
</style>