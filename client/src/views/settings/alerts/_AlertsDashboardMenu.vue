<template>
  <div>
    <div class="sidenav sidenav__background">
      <div>
        <h2 class="title">Smart Alerts</h2>
      </div>
      <router-link exact-active-class="active" :to="{ name: 'CreateNew' }">
        <div class="row">
          <img
            src="@/assets/images/template.png"
            style="height: 1rem; margin-right: 0.5rem"
            alt=""
          />
          <h3>Templates</h3>
        </div>
      </router-link>

      <router-link exact-active-class="active" :to="{ name: 'BuildYourOwn' }">
        <div class="row">
          <img src="@/assets/images/build.png" style="height: 1rem; margin-right: 0.5rem" alt="" />
          <h3>Build your own</h3>
        </div>
      </router-link>

      <router-link exact-active-class="active" :to="{ name: 'ListTemplates' }">
        <div class="row">
          <img src="@/assets/images/edit.png" style="height: 1rem; margin-right: 0.5rem" alt="" />
          <h3>Run/Activate</h3>
        </div>
      </router-link>

      <div>
        <div class="row" style="cursor: not-allowed">
          <img
            src="@/assets/images/analyze.png"
            style="height: 1.25rem; margin-right: 0.5rem"
            alt=""
          />
          <h3>Analyze <span class="coming-soon">coming soon</span></h3>
        </div>
      </div>
    </div>

    <div v-if="isHome" style="margin-left: 6vw">
      <h2 class="center" style="color: white">Smart Alerts</h2>
      <p class="center" style="font-weight: bold; color: #beb5cc; margin-top: -0.5rem">
        Automated workflows that help keep you on track
      </p>

      <div class="center" style="margin-top: 2rem">
        <SlackMessagePreview />
        <!-- <p style="color: #3c3940; align-self: flex-end; width: 30%">Ex.</p> -->
      </div>
    </div>

    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
import SlackMessagePreview from '@/views/settings/alerts/create/SlackMessagePreview'

export default {
  name: 'AlertsDashboardMenu',
  components: {
    SlackMessagePreview,
  },
  computed: {
    isHome() {
      return this.$route.name == 'alerts'
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.coming-soon {
  @include muted-font(13px);
}
.center {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}
.sidenav {
  height: 100%;
  width: 15vw;
  position: fixed;
  z-index: 1;
  left: 0;
  background-color: $panther;
  border: 2px solid $panther-silver;
  border-radius: 0.25rem;
  color: $panther-silver;
  overflow-x: hidden;
  padding-top: 20px;
  padding: 1rem;
  border-radius: 0.5rem;
}
a {
  text-decoration: none;
  font-weight: bold;
  color: $panther-silver;
  cursor: pointer;
}
a:hover {
  color: white;
  cursor: pointer;
}
.active {
  color: $dark-green;
  font-weight: bold;
}
.title {
  color: white;
  font-weight: bold;
}
.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}
</style>
