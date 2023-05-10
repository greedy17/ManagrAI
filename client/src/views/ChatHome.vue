<template>
  <div :class="{ background: showBackground }" id="chat">
    <div @click="toggleSidebar" class="hamburger">
      <font-awesome-icon style="height: 22px; width: 22px" icon="fa-solid fa-bars" />
    </div>
    <aside id="left-sidebar">
      <LeftSideBar
        ref="sidebarRef"
        @show-background="toggleBackgroundOn"
        @hide-background="toggleBackgroundOff"
      />
    </aside>
    <main id="main">
      <ChatBox />
    </main>
    <aside id="right-sidebar"></aside>
  </div>
</template>

<script>
import ChatBox from '../components/Chat/ChatBox.vue'
import LeftSideBar from '../components/Chat/LeftSideBar.vue'

export default {
  name: 'Home',
  components: {
    ChatBox,
    LeftSideBar,
  },
  data() {
    return {
      showBackground: false,
    }
  },
  created() {},
  watch: {},
  methods: {
    toggleSidebar() {
      this.$refs.sidebarRef.toggleSidebar()
    },
    toggleBackgroundOn() {
      this.showBackground = true
    },
    toggleBackgroundOff() {
      this.showBackground = false
    },
  },
  computed: {},
}
</script>

<style lang="scss">
@import '@/styles/variables';
@import '@/styles/buttons';
@import '@/styles/cards';
@import '@/styles/mixins/utils';
@import '@/styles/mixins/inputs';

body {
  overflow: auto;
  margin: 0;
  height: 100vh;
  width: 100vw;
  background-color: $off-white;
}

#chat {
  height: 100vh;
  width: 100vw;
  display: flex;
  font-family: $chat-font-family;
  color: $chat-font-color;
}

.hamburger {
  display: none;
  height: 50px;
  width: 50px;
  position: fixed;
  top: 1rem;
  left: 1.75rem;
  cursor: pointer;
}

#left-sidebar {
  width: 260px;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0.5rem;
}
#main {
  flex: 1;
  width: 54vw;
}

#right-sidebar {
  width: 28vw;
  border-left: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0.5rem;
}

@media (max-width: 820px) {
  #chat {
    flex-direction: column;
  }

  .hamburger {
    display: block;
  }

  #left-sidebar {
    position: absolute;
    /* styles for mobile sidebar */
  }

  #main {
    order: 2;
    width: 100%;
    height: 75%;
  }

  #right-sidebar {
    width: 100%;
    height: 25%;
    order: 1;
    /* styles for mobile sidebar "top bar" */
  }
}

@media (min-width: 820px) {
  .background {
    background-color: transparent !important;
  }

  .background::after {
    position: relative;
    background-color: transparent !important;
  }
}

.background {
  position: relative;
}

.background::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5); /* Adjust the opacity by modifying the last value */
  pointer-events: none; /* Allow click events to pass through to the children */
  z-index: 100; /* Ensure the overlay appears above the children */
}
</style>
