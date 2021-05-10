<template>
  <div>
    <div class="integrations__cards">
      <div @click="$router.push({ name: 'CreateNew' })" class="card">
        <div class="card__header">
          <img class="card-img" src="" />
          <h3 class="card__title">Create</h3>
        </div>

        <p class="card-text">Create a New Alert</p>
      </div>
      <div @click="$router.push({ name: 'ListTemplates' })" class="card">
        <div class="card__header">
          <img class="card-img" src="" />
          <h3 class="card__title">View</h3>
        </div>

        <p class="card-text">View & Edit Existing Alerts</p>
      </div>

      <div class="card">
        <div class="card__header">
          <img class="card-img" src="" />
          <h3 class="card__title">Instances</h3>
        </div>

        <p class="card-text">See how many times your alert was triggered</p>
      </div>
    </div>
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
export default {
  name: 'AlertsDashboardMenu',
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';
.integrations {
  display: flex;
  flex-direction: column;

  &__cards {
    display: flex;
    flex-wrap: wrap;
  }
  &__subtitle {
    font-size: 14px;
    margin-bottom: 2rem;
  }
}

.card {
  width: 10rem;
  margin-right: 1rem;
  margin-bottom: 2rem;
  &:hover {
    -moz-box-shadow: 0 0 5px 0.1rem $dark-green;
    -webkit-box-shadow: 0 0 5px 0.1rem $dark-green;
    box-shadow: 0 0 5px 0.1rem $dark-green;
    cursor: pointer;
  }
  @media only screen and (min-width: 768px) {
    flex: 1 0 24%;
    min-width: 21rem;
    max-width: 30rem;
  }

  &__header {
    display: flex;

    align-items: center;

    height: 5rem;
  }

  &__title {
    margin: 0 0 0 1rem;
  }
}
</style>
