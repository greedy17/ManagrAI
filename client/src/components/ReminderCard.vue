<template>
  <div class="notificaion-container">
    <div class="notification-card">
      <div class="notification-card__title">
        <span @click="toggleCard" class="notification-card__title__text">{{ reminder.title }}</span>
        <span @click.prevent="$emit('delete', reminder.id)" class="notification-card__title__type">
          <svg class="icon-notification">
            <use xlink:href="@/assets/images/remove.svg#remove" />
          </svg>
        </span>
      </div>
      <div class="notification-card__content" :class="{ expand: expand }">
        <span class="muted">{{ reminder.datetimeFor | dateShortWithTime }}</span>
        <span>{{ reminder.content }}</span>
        <div
          @click.prevent="goToLead(reminder.createdFor)"
          class="notification-card__content__leads"
        >
          {{ reminder.createdForRef.title }}
        </div>
      </div>
      <div class="notification-card__footer" :class="{ expand: expand }">
        <span class="notification-card__footer__type">
          REMINDER
        </span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ReminderCard',
  props: {
    reminder: {
      type: [Object, null],
      default: null,
    },
  },
  computed: {
    showSideNav() {
      return this.$store.getters.showSideNav
    },
  },
  data() {
    return {
      expand: false,
    }
  },
  created() {},
  methods: {
    toggleNotifications() {
      this.$store.commit('TOGGLE_SIDE_NAV', !this.showSideNav)
    },
    toggleCard() {
      this.expand = !this.expand
    },

    goToLead(id) {
      let nextRoute = this.$router.resolve({ name: 'LeadsDetail', params: { id: id } }).route
      // avoid redundant route redirect if on current page
      if (this.$route.path !== nextRoute.path) {
        this.$router.push({ params: nextRoute.params, name: nextRoute.name })
      }

      this.toggleNotifications()
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/sidebars';
@import '@/styles/variables';
.notification-card {
  @include card();
  &:hover {
    cursor: pointer;
  }
  &__title {
    display: flex;
    overflow: hidden;
    text-transform: capitalize;

    &__text {
      flex: 1 0 auto;
      max-width: 12vw;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }
    &__type {
    }
  }
  &__content {
    display: none;
    justify-content: center;
    flex-direction: column;
    overflow: hidden;

    &__leads {
      display: flex;
      justify-content: flex-end;
      text-decoration: underline;

      &:hover {
        color: blue;
      }
    }
  }
  &__footer {
    display: none;
    justify-content: flex-end;

    &__type {
      color: darken($soft-gray, 15%);
    }
  }
}
.expand {
  display: flex;
}
.icon-notification {
  width: 25px;
  height: 20px;
}
.unviewed {
  background-color: $item-active;
}
</style>
