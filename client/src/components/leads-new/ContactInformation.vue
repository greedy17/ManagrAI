<template>
  <div class="contact-information">
    <div class="container">
      <img class="image" src="@/assets/images/sara-smith.png" alt="contact image" />
      <span>{{ contact.fullName }}</span>
    </div>
    <div class="container background-color">
      <img class="icon" src="@/assets/images/contact.svg" alt="icon" />
      <span>{{ contact.title }}</span>
    </div>
    <div class="container background-color">
      <img class="icon" src="@/assets/images/telephone.svg" alt="icon" />
      <span class="contact-phone-number">{{ contact.phone }}</span>
    </div>
    <div class="container background-color">
      <img class="icon" src="@/assets/images/email.svg" alt="icon" />
      <span class="contact-email">{{ contact.email }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ContactInformation',
  props: {
    contact: {
      required: true,
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.contact-information {
  display: flex;
  flex-flow: column;
  box-sizing: border-box;
  padding-left: 0.5rem;
  margin-bottom: 1rem;

  font-family: $base-font-family, $backup-base-font-family;
}

.container {
  display: flex;
  flex-flow: row;
  align-items: center;
  margin-bottom: 0.2rem;
  padding-right: 1rem;
  padding-left: 0.5rem;
  border-radius: 0.3rem;
  height: 2rem;
}

.background-color {
  background-color: rgba($color: $light-gray-blue, $alpha: 0.2);
}

.image {
  height: 1.4rem;
  width: 1.4rem;
  border-radius: 50%;
  margin-right: 1rem;
}

.icon {
  height: 1.4rem;
  width: 1.4rem;
  margin-right: 1rem;
}
</style>
