<template>
  <div class="sidebar" :class="{ open: isOpen }">
    <section>
      <header>
        <button class="primary-button">
          <font-awesome-icon icon="fa-solid fa-rocket" />
          <span> Start New Thread</span>
        </button>
      </header>

      <div class="body"></div>

      <footer>
        <button class="secondary-button">
          <font-awesome-icon icon="fa-solid fa-cog" />
          <span>Configure</span>
        </button>
        <button class="secondary-button">
          <font-awesome-icon icon="fa-solid fa-headphones" />
          <span> Contact Support</span>
        </button>
        <button class="secondary-button">
          <font-awesome-icon icon="fa-solid fa-user" />
          <span> Profile & Team </span>
        </button>
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
  components: {},
  data() {
    return {
      isOpen: false,
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
  overflow-x: hidden;
  transition: all 0.3s ease;

  &.open {
    left: 0;
  }

  section {
    padding: 1rem;
    // Add your nav styles here
  }
}

@media (max-width: 820px) {
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

@media (min-height: 1025px) {
  .body {
    height: 78vh;
  }
}
@media (max-height: 600px) {
  .body {
    height: 56vh;
  }
}

@media (min-height: 850px), (max-height: 1200px) {
  .body {
    height: 70vh;
  }
}

@media (min-height: 1200px) {
  .body {
    height: 78vh;
  }
}

footer {
  height: 20vh;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 0.5rem 0rem;
}

.primary-button {
  @include chat-button();
  width: 100%;
  margin: 0.5rem 0;
  font-size: 14px;
  font-family: $chat-font-family;
  color: white;
  background-color: $dark-blue;

  span {
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
  }
}

.secondary-button {
  @include chat-button();
  width: 100%;
  margin: 0.5rem 0;
  font-size: 14px;
  font-family: $chat-font-family;
  color: $chat-font-color;

  span {
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
  }
}

svg {
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