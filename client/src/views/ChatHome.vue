<template>
  <div id="chat" class="chat-display">
    <h1>Hello world, chat here.</h1>
    <div style="height: 90vh;">
      <ChatBox />
    </div>
    <RightBar />
  </div>
</template>

<script>
import ChatBox from '../components/Chat/ChatBox.vue';
import RightBar from '../components/Chat/RightBar.vue';

export default {
  name: 'Home',
  components: {
    ChatBox,
    RightBar,
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

.chat-display {
  display: flex;
}
</style>
