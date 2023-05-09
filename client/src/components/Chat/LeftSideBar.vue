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
  props: {
    type: {
      type: String,
      default: 'full',
    },
  },
  methods: {
    toggleSidebar() {
      this.isOpen = !this.isOpen
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
  width: 18vw;
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

@media (max-width: 768px) {
  .sidebar {
    left: -250px;

    &.open {
      left: 0;
    }
  }
}

header {
}

.body {
  height: 66vh;
  overflow-y: scroll;
  overflow-x: hidden;
  text-overflow: ellipsis;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
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
  transition: all 0.2s ease;

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
  transition: all 0.2s ease;

  span {
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
  }
}

svg {
  margin-right: 1rem;
}
</style>