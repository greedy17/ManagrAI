<template>
  <div class="sidebar" :class="{ open: isOpen }">
    <section>
      <header>
        <button @mouseenter="soonThreadText" @mouseleave="newThreadText" class="primary-button">
          <!-- <font-awesome-icon style="color: #183153" icon="fa-solid fa-rocket" /> -->
          <span style="font-size: 14px; margin-right: 1rem">🚀</span>
          <span> {{ threadButtonText }}</span>
        </button>
      </header>

      <div class="body"></div>

      <footer>
        <button class="secondary-button">
          <!-- <font-awesome-icon icon="fa-solid fa-cog" /> -->
          <img style="margin-left: -2px" src="@/assets/images/settings.svg" height="18px" alt="" />
          <span>Configure</span>
        </button>
        <button class="secondary-button">
          <img src="@/assets/images/help.png" height="14px" alt="" />
          <span> Contact Support</span>
        </button>
        <button class="secondary-button" @click="handleProfileOpen">
          <img src="@/assets/images/profile.svg" height="14px" alt="" />
          <span> Profile & Team </span>
        </button>

        <!-- <div class="tooltip">

        </div> -->
      </footer>
    </section>

    <div @click="toggleSidebar" v-if="isOpen" class="close">
      <font-awesome-icon
        style="height: 30px; width: 30px; color: white"
        icon="fa-solid fa-square-xmark"
      />
    </div>
  </div>
</template>

<script>
export default {
  name: 'LeftSideBar',
  props: {
    handleProfileOpen: { type: Function },
  },
  data() {
    return {
      isOpen: false,
      threadButtonText: 'Start New Thread',
    }
  },
  methods: {
    toggleSidebar() {
      this.isOpen = !this.isOpen

      if (this.isOpen) {
        this.$emit('show-background')
      } else {
        this.$emit('hide-background')
      }
    },
    soonThreadText() {
      this.threadButtonText = 'Coming Soon!'
    },
    newThreadText() {
      this.threadButtonText = 'Start New Thread'
    },
  },
  computed: {},
  created() {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';
@import '@/styles/cards';
@import '@/styles/mixins/utils';
@import '@/styles/mixins/inputs';

.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100%;
  width: 260px;
  overflow: auto;
  transition: all 0.3s ease;
  letter-spacing: 0.4px;
  font-size: 14px;

  &.open {
    left: 0;
  }

  section {
    padding: 1rem;
    // Add your nav styles here
  }
}

@media (max-width: 1000px) {
  .sidebar {
    left: -250px;

    &.open {
      left: 0;
      z-index: 999;
      background-color: $off-white;
    }
  }

  .close {
    display: block !important;
  }
}

.body {
  height: 66vh;
  overflow-y: scroll;
  overflow-x: hidden;
  text-overflow: ellipsis;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

@media (max-height: 600px) {
  .body {
    height: 56vh;
  }
}

@media (max-height: 750px) {
  .body {
    height: 66vh;
  }
}

@media (min-height: 875px) {
  .body {
    height: 70vh;
  }
}

@media (min-height: 1025px) {
  .body {
    height: 75vh;
  }
}

@media (min-height: 1200px) {
  .body {
    height: 78vh;
  }
}

footer {
  height: 20vh;
  position: absolute;
  bottom: 1.5rem;
  width: 230px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 0.5rem 0rem;
}

.primary-button {
  @include chat-button();
  width: 100%;
  margin-bottom: 0.5rem;
  font-size: 12px;
  color: white;
  background-color: $base-gray;

  span {
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
    font-family: $base-font-family;
  }

  &:hover {
    cursor: not-allowed;
    opacity: 0.8;
    scale: none;
  }
}

.secondary-button {
  @include chat-button();
  width: 100%;
  margin-bottom: 0.5rem;
  font-size: 14px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);

  span {
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
  }
}

svg,
img {
  margin-right: 1rem;
}

.close {
  position: inherit;
  top: 0;
  left: 280px;
  top: 1.5rem;
  display: none;
  cursor: pointer;
}
</style>