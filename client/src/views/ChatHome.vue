<template>
  <div id="chat">
    <h1>Hello world, chat here.</h1>
    <ChatBox />
  </div>
</template>

<script>
import ChatBox from '../components/Chat/ChatBox.vue';

export default {
  name: 'Home',
  components: {
    ChatBox
  },
  data() {
    return {}
  },

  created() {},

  methods: {},
  computed: {},
}
</script>

<style lang="scss">
@import '@/styles/variables';
@import '@/styles/buttons';
@import '@/styles/cards';
@import '@/styles/mixins/utils';
@import '@/styles/mixins/inputs';
.Vue-Toastification__toast--success.custom {
  background-color: $dark-green;
}
.Vue-Toastification__toast--default.custom {
  background-color: $base-gray;
}
* {
  box-sizing: border-box;
}

body {
  overflow: auto;
  margin: 0;
  min-height: 100vh;
  background-color: $off-white;
}
</style>
