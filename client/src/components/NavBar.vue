<template>
  <div>
    <div v-if="userIsLoggedIn">
      <nav id="nav" v-if="isPR">
        <router-link :to="{ name: 'PRSummaries' }">
          <div class="logo">
            <img style="height: 32px" src="@/assets/images/logo.png" />
          </div>
        </router-link>

        <div class="input">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path
              fill-rule="evenodd"
              clip-rule="evenodd"
              d="M4.1 11.06a6.95 6.95 0 1 1 13.9 0 6.95 6.95 0 0 1-13.9 0zm6.94-8.05a8.05 8.05 0 1 0 5.13 14.26l3.75 3.75a.56.56 0 1 0 .8-.79l-3.74-3.73A8.05 8.05 0 0 0 11.04 3v.01z"
              fill="currentColor"
            ></path>
          </svg>
          <!-- @keydown.enter="loadFromEnter" -->
          <input class="search-input" v-model="searchText" :placeholder="`Search...`" />
          <img
            v-show="searchText"
            @click="clearText"
            src="@/assets/images/close.svg"
            class="invert"
            height="12px"
            alt=""
          />
        </div>

        <div class="auto-left">
          <!-- <router-link active-class="active" :to="{ name: 'PRSummaries' }">
            <img src="@/assets/images/search-alt.svg" class="nav-img" height="16px" alt="" />
          </router-link> -->
          <!-- <router-link active-class="active" :to="{ name: 'PRClipReport' }">
            <img src="@/assets/images/file-excel.svg" class="nav-img" height="16px" alt="" />
          </router-link> -->
          <div class="row right-mar">
            <div class="avatar">{{ userName[0] }}</div>
            <img src="@/assets/images/downArrow.svg" height="14px" alt="" />
          </div>

          <!-- <router-link :to="{ name: 'Login' }">
            <div>
              <img @click="logOut" src="@/assets/images/logout.svg" alt="" height="16px" />
            </div>
          </router-link> -->
        </div>
      </nav>
    </div>
  </div>
</template>

<script>
import { CollectionManager } from '@thinknimble/tn-models'
import { decryptData } from '../encryption'

export default {
  name: 'NavBar',
  components: {
    CollectionManager,
  },
  data() {
    return {
      items: [],
      searchText: null,
    }
  },

  methods: {
    logOut() {
      this.$store.dispatch('logoutUser')
      this.$router.push({ name: 'Login' })
    },
    openModal() {
      this.modalOpen = true
    },
    closeModal() {
      this.modalOpen = false
    },
    clearText() {
      this.searchText = ''
    },
  },
  computed: {
    userName() {
      return this.$store.state.user.firstName
    },
    isPR() {
      return this.$store.state.user.role === 'PR'
    },
    userIsLoggedIn() {
      return this.$store.getters.userIsLoggedIn
    },
    userCRM() {
      return this.$store.state.user.crm
    },
    routeName() {
      return this.$route.name
    },
    isAdmin() {
      return this.userIsLoggedIn && this.$store.state.user.isAdmin
    },
    isTeamLead() {
      return this.userIsLoggedIn && this.$store.state.user.isTeamLead
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/modals';

@media only screen and (max-width: 600px) {
}
/* Small devices (portrait tablets and large phones, 600px and up) */
@media only screen and (min-width: 600px) {
}
/* Medium devices (landscape tablets, 768px and up) */
@media only screen and (min-width: 768px) {
}
/* Large devices (laptops/desktops, 992px and up) */
@media only screen and (min-width: 992px) {
}
/* Extra large devices (large laptops and desktops, 1200px and up) */
@media only screen and (min-width: 1200px) {
}

@keyframes tooltips-horz {
  to {
    opacity: 0.9;
    transform: translate(10%, 0%);
  }
}
.row {
  display: flex;
  align-items: center;
  flex-direction: row;
}

.right-mar {
  margin-right: 1.25rem;
}

::placeholder {
  color: rgba(0, 0, 0, 0.4);
}

.input {
  width: 300px;
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-family: $base-font-family;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 8px 20px 8px 10px;
}

.search-input {
  border: none;
  outline: none;
  margin-left: 0.5rem;
  width: 100%;
}

.avatar {
  background-color: $soft-gray;
  color: $base-gray;
  font-size: 12px;
  width: 32px;
  height: 32px;
  margin-right: 4px;
  border-radius: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-img {
  height: 16px;
}
div > span {
  font-size: 11px;
  color: $dark-green;
  background-color: #f3f0f0;
  margin-left: 0.25rem;
  padding: 0.2rem;
  border-radius: 0.2rem;
}
nav {
  width: 100vw;
  display: flex;
  flex-direction: row;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 2000;
  height: 58px;
  background-color: white;
  padding: 0px 4px;
  border-bottom: 1px solid $soft-gray;
}
.logo {
  cursor: pointer;
  filter: brightness(0%) invert(65%) sepia(7%) saturate(2970%) hue-rotate(101deg) brightness(94%)
    contrast(89%);
  margin-right: 0.5rem;
}

.auto-left {
  margin-left: auto;
  display: flex;
  align-items: center;
  flex-direction: row;
  gap: 16px;
}

a {
  text-decoration: none;
  color: $base-gray;
  font-family: #{$base-font-family};
  font-weight: bold;
  // padding: 16px 12px;
  padding: 12px 12px 10px 12px;
  img {
    transition: all 0.2s;
  }
}
a:hover {
  color: white;
}
.active {
  background-color: $white-green;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 5px;
  img {
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
  }
}
</style>
