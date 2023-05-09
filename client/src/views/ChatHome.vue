<template>
  <div id="chat">
    <div @click="toggleSidebar" class="hamburger">
      <font-awesome-icon style="height: 22px; width: 22px" icon="fa-solid fa-bars" />
    </div>
    <aside id="left-sidebar">
      <LeftSideBar ref="sidebarRef" :type="sideBarType" />
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
      sideBarType: null,
    }
  },
  created() {},
  methods: {
    toggleSidebar() {
      this.$refs.sidebarRef.toggleSidebar()
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
}

#left-sidebar {
  width: 18vw;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0.5rem;
}
#main {
  flex-grow: 1;
  width: 52vw;
}

#right-sidebar {
  width: 30vw;
  border-left: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0.5rem;
}

@media (max-width: 768px) {
  #chat {
    flex-direction: column;
  }

  .hamburger {
    display: block;
  }

  #left-sidebar {
    width: 100%;
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
</style>
