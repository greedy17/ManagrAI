<template>
  <div>
    <div v-if="userIsLoggedIn">
      <nav id="nav" v-if="isPR">
        <router-link :to="{ name: 'PRSummaries' }">
          <div @click="goHome" class="logo">
            <img style="height: 28px" src="@/assets/images/logo.png" />
          </div>
        </router-link>

        <router-link active-class="active" :to="{ name: 'PRSummaries' }">
          <p>Digest</p>
        </router-link>

        <router-link active-class="active" :to="{ name: 'Pitches' }">
          <p>Pitch</p>
        </router-link>

        <router-link :to="{ name: 'PRSummaries' }">
          <p>Transcribe</p>
        </router-link>

        <!-- <div class="input">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path
              fill-rule="evenodd"
              clip-rule="evenodd"
              d="M4.1 11.06a6.95 6.95 0 1 1 13.9 0 6.95 6.95 0 0 1-13.9 0zm6.94-8.05a8.05 8.05 0 1 0 5.13 14.26l3.75 3.75a.56.56 0 1 0 .8-.79l-3.74-3.73A8.05 8.05 0 0 0 11.04 3v.01z"
              fill="currentColor"
            ></path>
          </svg>
          <input class="search-input" v-model="searchText" :placeholder="`Search...`" />
          <img
            v-show="searchText"
            @click="clearText"
            src="@/assets/images/close.svg"
            class="invert"
            height="12px"
            alt=""
          />
        </div> -->

        <div class="auto-left">
          <div class="relative">
            <div @click="toggleShowSearches" class="row pointer nav-text">
              Saved Searches
              <img src="@/assets/images/downArrow.svg" height="14px" alt="" />
            </div>

            <div v-if="showSavedSearches" class="search-dropdown">
              <p v-for="search in searches" :key="search.id" @click="selectSearch(search)">
                {{ search.name }}
              </p>
            </div>
          </div>

          <div class="row pointer">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-label="Lists">
              <path
                d="M6.44 6.69h0a1.5 1.5 0 0 1 1.06-.44h9c.4 0 .78.16 1.06.44l.35-.35-.35.35c.28.28.44.66.44 1.06v14l-5.7-4.4-.3-.23-.3.23-5.7 4.4v-14c0-.4.16-.78.44-1.06z"
                stroke="currentColor"
              ></path>
              <path
                d="M12.5 2.75h-8a2 2 0 0 0-2 2v11.5"
                stroke="currentColor"
                stroke-linecap="round"
              ></path>
            </svg>
          </div>

          <div class="row right-mar avatar-container">
            <div @click="toggleMenu" class="avatar">{{ userName[0] }}</div>
            <img
              @click="toggleMenu"
              class="pointer"
              src="@/assets/images/downArrow.svg"
              height="14px"
              alt=""
            />

            <div v-if="menuOpen" class="avatar-dropdown">
              <p class="dropdown-item">
                <img src="@/assets/images/profile.svg" height="14px" alt="" />
                Profile
              </p>
              <p class="dropdown-item">
                <img class="mar-right" src="@/assets/images/settings.svg" height="16px" alt="" />
                Settings
              </p>
              <p @click="logOut" class="dropdown-item__bottom">Sign out</p>
              <!-- 
              <router-link :to="{ name: 'Login' }">
                <div>
                  <img @click="logOut" src="@/assets/images/logout.svg" alt="" height="16px" />
                </div>
              </router-link> -->
            </div>
          </div>
        </div>
      </nav>
    </div>
  </div>
</template>

<script>
import { CollectionManager } from '@thinknimble/tn-models'

export default {
  name: 'NavBar',
  components: {
    CollectionManager,
  },
  data() {
    return {
      items: [],
      searchText: null,
      menuOpen: false,
      showSavedSearches: false,
    }
  },
  created() {
    this.getSearches()
  },
  methods: {
    selectSearch(search) {
      this.toggleShowSearches()
      this.$store.dispatch('setSearch', search)
    },
    toggleShowSearches() {
      this.showSavedSearches = !this.showSavedSearches
    },
    getSearches() {
      this.$store.dispatch('getSearches')
    },
    goHome() {
      this.$router.go()
    },
    toggleMenu() {
      this.menuOpen = !this.menuOpen
    },
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
    searches() {
      return this.$store.state.allSearches
    },
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

.relative {
  position: relative;
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

.avatar-container {
  position: relative;
}

.avatar-dropdown {
  width: 180px;
  position: absolute;
  top: 40px;
  right: -8px;
  font-size: 12px;
  font-weight: 400;
  background: white;
  padding: 1rem 0 0 0;
  border-radius: 5px;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
  z-index: 2000;
  border: 1px solid rgba(0, 0, 0, 0.1);

  p {
    margin-top: 8px;
    padding: 0;
  }
}

.search-dropdown {
  width: 220px;
  position: absolute;
  top: 40px;
  right: -8px;
  font-size: 12px;
  font-weight: 400;
  background: white;
  padding: 0;
  border-radius: 5px;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
  z-index: 2001;
  border: 1px solid rgba(0, 0, 0, 0.1);

  p {
    // background: red;
    padding: 8px 16px;
    font-size: 14px;
    color: #7c7b7b;
    cursor: pointer;
    width: 205px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    margin: 0;
  }

  p:hover {
    color: $dark-black-blue;
  }
}

.dropdown-item {
  display: flex;
  align-items: center;
  flex-direction: row;
  font-size: 14px;
  color: $dark-black-blue;
  padding: 2px 0 !important;
  padding-left: 1rem;
  cursor: pointer;
  position: relative;
  width: 100%;
  img {
    margin: 0 1.5rem 0 1.5rem;
  }

  p {
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
    width: 100%;
    margin: 0;
  }

  &:hover {
    opacity: 0.65;
  }

  &__bottom {
    font-size: 14px;
    padding-top: 8px !important;
    display: flex;
    align-items: center;
    justify-content: center;
    color: $dark-black-blue;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    cursor: pointer;

    &:hover {
      opacity: 0.65;
    }
  }
}

.mar-right {
  margin-right: 23px !important;
}

.pointer {
  cursor: pointer;
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
  cursor: pointer;
}
.left-mar {
  margin-left: 0.5rem;
  color: $dark-black-blue;
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
  display: flex;
  align-items: center;
  justify-content: center;
  img {
    filter: brightness(0) invert(48%) sepia(33%) saturate(348%) hue-rotate(161deg) brightness(91%)
      contrast(90%);
  }
  margin-right: 0.5rem;
}

.auto-left {
  margin-left: auto;
  display: flex;
  align-items: center;
  flex-direction: row;
  gap: 36px;
  font-weight: 300 !important;
  font-family: $base-font-family;
  font-size: 14px;
}

.off-gray {
  color: #6b6b6b;
}

.nav-text {
  font-weight: 400;
  font-family: $base-font-family;
  color: #6b6b6b;
  font-size: 14px;
  padding: 6px 0;
  img {
    margin-left: 8px;
  }
}

a {
  text-decoration: none;
  font-weight: 400;
  font-family: $base-font-family;
  // color: #6b6b6b;
  color: $light-gray-blue;
  font-size: 14px;
  padding: 6px 16px;
  img {
    transition: all 0.2s;
  }
}
a:hover {
  color: rgba(0, 0, 0, 0.5);
}
.active {
  color: #6b6b6b;
  position: relative;
}

.active::before {
  content: '';
  position: absolute;
  left: 16px;
  bottom: 0;
  height: 1px;
  width: 70%;
  border-bottom: 1px solid $mid-gray;
}
</style>
