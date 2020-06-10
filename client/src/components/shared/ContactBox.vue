<template>
  <!-- TODO: I don't know why the objectToCamelCase in services/leads is not  -->
  <!-- making the nested serializers camel case as well  -->
  <div class="contact-box" :class="{ 'contact-box--active': isActive }" @click="toggleActive()">
    <div class="contact-box__contact-circle-container">
      <div class="contact-box__contact-circle">
        {{ initials }}
      </div>
    </div>
    <div class="contact-box__contact-name-container">
      <div class="contact-box__contact-name">
        {{ contact.full_name }}
      </div>
    </div>
    <div class="contact-box__contact-number-container">
      <div class="contact-box__contact-icon">
        <img alt="icon" :src="require(`@/assets/images/telephone.svg`)" class="icon" />
      </div>
      <div class="contact-box__contact-number">
        {{ contact.phone_number_1 }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ContactContainer',
  components: {},
  props: {
    contact: {
      type: Object,
      required: true,
    },
    isActive: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    toggleActive() {
      this.$emit('toggle', this.contact.id)
    },
  },
  computed: {
    initials() {
      if (!this.contact.full_name) {
        return
      }
      let names = this.contact.full_name.split(' '),
        initials = names[0].substring(0, 1).toUpperCase()
      if (names.length > 1) {
        initials += names[names.length - 1].substring(0, 1).toUpperCase()
      }
      return initials
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/mixins/utils';
@import '@/styles/variables';
@import '@/styles/fonts';

.contact-box {
  @include standard-border();
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  border-radius: 0.5rem;
  &__contact-circle-container {
    flex: 1;
    line-height: 1rem;
    background-color: $dark-gray-blue;
    color: $white;
    font-weight: 1000;
    height: 2rem;
    width: 2rem;
    justify-content: center;
    align-items: center;
    display: flex;
    border-radius: 50%;
  }
  &__contact-circle {
  }
  &__contact-name-container {
    text-align: center;
    flex: 4;
  }
  &__contact-name {
  }
  &__contact-number-container {
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    text-align: center;
    background-color: $soft-gray;
    flex: 4;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  &__contact-number-icon {
  }
  &__contact-number {
  }
  &--active {
    border: 1px solid $dark-gray-blue;
  }
}
</style>
