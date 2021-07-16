<template>
  <div>
    <div class="integrations__cards">
      <div @click="$router.push({ name: 'CreateNew' })" class="card">
        <div class="card__header">
          <img class="card-img" src="@/assets/images/logo.png" />
          <h3 class="title">Build</h3>
        </div>

        <p class="sub">Build alerts that help keep you proactive.</p>
      </div>
      <div @click="$router.push({ name: 'ListTemplates' })" class="card">
        <div class="card__header">
          <img class="card-img" src="@/assets/images/logo.png" />
          <h3 class="title">View</h3>
        </div>

        <p class="sub">View & Edit Existing Alerts</p>
      </div>

      <div class="card card--disabled">
        <div class="card__header">
          <img class="card-img" src="@/assets/images/logo.png" />
          <h3 class="title">Analyze</h3>
        </div>

        <p class="card-text">See how many times your alert was triggered</p>
        <p class="coming-soon">Coming Soon</p>
      </div>
    </div>
    <router-view :key="$route.fullPath"></router-view>
    <div class="center">
      <p class="gray">
        <strong class="pink">Note:</strong> Smart Alerts are fully customizable and will be sent to
        your slack channels based on how you set them up here.
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AlertsDashboardMenu',
  // data() {
  //   return {
  //     showBuild: false,
  //     showView: false,
  //     showAnalyze: false,
  //   }
  // },
  // methods: {
  //   showBuildText() {
  //     this.showBuild = !this.showBuild
  //   },
  //   showViewText() {
  //     this.showView = !this.showView
  //   },
  //   showAnalyzeText() {
  //     this.showAnalyze = !this.showAnalyze
  //   },
  // },
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
.coming-soon {
  @include muted-font(13px);
}

.card {
  width: 10rem;

  margin-right: 1rem;
  margin-bottom: 2rem;
  margin-top: 1rem;
  background: linear-gradient($grape, #231049);
  color: $soft-gray;
  border-radius: 1rem;
  transition: all 0.5s ease-in-out;
  &:hover {
    -moz-box-shadow: 0 4px 8px 2px $grape;
    -webkit-box-shadow: 0 4px 8px 2px $grape;
    box-shadow: 0 4px 8px 2px $grape;
    transform: scale(1.05);
    font-size: 1.025rem;
    color: $off-white;
    cursor: pointer;
  }
  &--disabled {
    &:hover {
      -moz-box-shadow: 0 0 5px 0.1rem gray;
      -webkit-box-shadow: 0 0 5px 0.1rem gray;
      box-shadow: 0 0 5px 0.1rem gray;
      cursor: not-allowed;
    }
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
    border-bottom: 1px solid gray;
  }

  &__title {
    margin: 0 0 0 1rem;
  }
}
img {
  height: 1.75rem;
}
.title {
  font-weight: bold;
  font-size: 1.5rem;
}
.active {
  border-bottom: 3px solid $grape;
  padding-bottom: 1rem;
  color: $grape;
}
.sub {
  font-size: 1.2rem;
  font-weight: bold;
  text-align: center;
}
.gray {
  color: $gray;
  text-align: center;
}
.pink {
  color: $candy;
}
</style>
