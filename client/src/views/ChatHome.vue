<template>
  <div id="chat">
    <div class="hamburger"></div>
    <aside id="left-sidebar">
      <!-- LeftSideBar ref="sidebarRef" @click="toggleSidebar" :type='sideBarType'  /> -->
      <p>left</p>
    </aside>
    <main id="main">
      <h3>*Chat box component will go here*</h3>
    </main>
    <aside id="right-sidebar">
      <p>right</p>
    </aside>
  </div>
</template>

<script>
export default {
  name: 'Home',
  components: {},
  data() {
    return {
      sideBarType: 'normal',
    }
  },
  created() {},
  methods: {
    // toggleSidebar() {
    //   this.$refs.sidebarRef.toggleSidebar();
    // }
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
  background-color: purple;
  display: none;
  height: 50px;
  width: 50px;
  position: fixed;
  top: 0;
  left: 0;
}

#left-sidebar {
  width: 18vw;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
}
#main {
  flex-grow: 1;
}

#right-sidebar {
  width: 30vw;
  border-left: 1px solid rgba(0, 0, 0, 0.1);
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
  }

  #right-sidebar {
    width: 100%;
    height: 20%;
    order: 1;
    background-color: red;
    /* styles for mobile sidebar "top bar" */
  }
}
</style>
