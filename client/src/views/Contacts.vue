<template>
  <div class="contacts">
    <header>
      <!-- <h2>Your library of Journalists</h2> -->
    </header>

    <div class="space-between">
      <div class="row">
        <div style="margin-right: 16px" class="relative">
          <button
            style="padding-top: 11px; padding-bottom: 11px"
            @click="toggleUserDropdown"
            class="secondary-button"
          >
            <img style="margin-right: 8px" src="@/assets/images/profile.svg" height="12px" alt="" />
            {{
              !selectedUser
                ? 'All'
                : selectedUser.fullName
                ? selectedUser.fullName
                : selectedUser.full_name
            }}
            <img style="margin-left: 8px" src="@/assets/images/dropdown.svg" height="14px" alt="" />
          </button>

          <div style="left: 0" v-if="showUsers" class="dropdown">
            <div class="dropdown-header">
              <h3>Select User</h3>
              <img
                @click="toggleUserDropdown"
                src="@/assets/images/close.svg"
                class="pointer"
                height="18px"
                alt=""
              />
            </div>

            <div style="margin: 8px 0 16px 0; padding-right: 12px">
              <div style="width: 100%" class="input">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                  <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M4.1 11.06a6.95 6.95 0 1 1 13.9 0 6.95 6.95 0 0 1-13.9 0zm6.94-8.05a8.05 8.05 0 1 0 5.13 14.26l3.75 3.75a.56.56 0 1 0 .8-.79l-3.74-3.73A8.05 8.05 0 0 0 11.04 3v.01z"
                    fill="currentColor"
                  ></path>
                </svg>
                <input v-model="searchUsersText" class="search-input" :placeholder="`Search...`" />
                <img
                  v-if="searchUsersText"
                  @click="clearUsersText"
                  src="@/assets/images/close.svg"
                  class="pointer"
                  height="12px"
                  alt=""
                />
              </div>
            </div>

            <div class="dropdown-body">
              <div class="col">
                <div v-if="!searchUsersText" @click="selectAllUsers" class="dropdown-item">All</div>
                <div
                  @click="selectUser(user)"
                  class="dropdown-item"
                  v-for="(user, i) in allUsers"
                  :key="i"
                >
                  {{ user.full_name }}
                </div>
              </div>
            </div>

            <div class="dropdown-footer"></div>
          </div>
        </div>
      </div>

      <div class="search">
        <div class="input">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path
              fill-rule="evenodd"
              clip-rule="evenodd"
              d="M4.1 11.06a6.95 6.95 0 1 1 13.9 0 6.95 6.95 0 0 1-13.9 0zm6.94-8.05a8.05 8.05 0 1 0 5.13 14.26l3.75 3.75a.56.56 0 1 0 .8-.79l-3.74-3.73A8.05 8.05 0 0 0 11.04 3v.01z"
              fill="currentColor"
            ></path>
          </svg>
          <input
            v-model="searchContactsText"
            class="search-input"
            :placeholder="`Search contacts...`"
          />
          <img
            v-if="searchContactsText"
            @click="clearSearchText"
            src="@/assets/images/close.svg"
            class="pointer"
            height="12px"
            alt=""
          />
        </div>
      </div>
    </div>

    <div class="top-row top-padding">
      <aside>
        <div style="margin-left: 2px" class="row">
          <img src="@/assets/images/tags.svg" height="14px" alt="" />
          <h3>Tags</h3>
        </div>

        <div class="checkbox-list">
          <ul>
            <li v-for="(tag, i) in tags" :key="i">
              <label>
                <input type="checkbox" :value="tag" v-model="selectedTags" />
                {{ tag }} (3)
              </label>
            </li>
          </ul>
        </div>
      </aside>

      <section>
        <div>
          <h3 style="font-size: 16px">Showing: 6 contacts</h3>
        </div>

        <div class="cards-container">
          <div class="contact-card">
            <header>
              <div>
                <p>Firstname Lastname</p>
                <section>
                  <!-- <img src="@/assets/images/building.svg" height="13px" alt="" /> -->
                  OutletName
                </section>
              </div>
              <div style="display: flex; flex-direction: row; justify-content: flex-end">
                <img class="main-img" src="" alt="" />
                <img class="main-img" src="" alt="" />
                <img class="main-img" src="" alt="" />
              </div>
            </header>

            <div class="body">
              <p>
                Bio here lorem ipsum. Bio here lorem ipsum. Bio here lorem ipsum. Bio here lorem
                ipsum. Bio here lorem ipsum. Bio here lorem ipsum. Bio here lorem ipsum. Bio here
                lorem ipsum. Bio here lorem ipsum. Bio here lor ipsum. g et bgr bdtel blersnblte tb
                dljnejbv jrwbejr bio her lorwm ips
              </p>
              <div class="blur"></div>
              <div class="more">
                Read More <img src="@/assets/images/rightarrow.svg" height="12px" alt="" />
              </div>
            </div>

            <div class="footer">
              <div class="row">
                <button style="padding-left: 8px" class="secondary-button">
                  <img
                    style="margin-right: 2px"
                    src="@/assets/images/add.svg"
                    height="14px"
                    alt=""
                  />
                  Tag
                </button>
                <button class="primary-button">Pitch</button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import User from '@/services/users'
import { Comms } from '@/services/comms'

export default {
  name: 'Contacts',
  components: {
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
  },
  data() {
    return {
      showUsers: false,
      selectedUser: null,
      searchUsersText: '',
      searchContactsText: '',
      users: [],
      showList: false,
      contacts: [],
      tags: ['Test', 'Hello', 'World', 'Tags', 'Will', 'Appear', 'Right Here'],
      newTag: '',
      contactId: null,
      modifier: 'add',
      selectedTags: [],
    }
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    allUsers() {
      return this.users.filter((user) =>
        user.full_name.toLowerCase().includes(this.searchUsersText),
      )
    },
  },
  mounted() {},
  created() {
    this.selectedUser = this.user
    this.getUsers()
    this.getContacts()
    this.getTags()
  },
  methods: {
    toggleUserDropdown() {
      this.showUsers = !this.showUsers
    },
    toggleListDropdown() {
      this.showList = !this.showList
    },
    async getUsers() {
      try {
        const res = await User.api.getAllUsers()
        this.users = res.results.filter((user) => user.organization == this.user.organization)
      } catch (e) {
        console.log('Error in getTrialUsers', e)
      }
    },
    async getContacts() {
      try {
        const res = await Comms.api.getContacts()
        console.log('contacts here :', res)
        // this.contacts = res.results
      } catch (e) {
        console.error(e)
      }
    },
    async getTags() {
      try {
        const res = await Comms.api.getContactTagList()
        console.log('tags here :', res)
        // this.tags = res.tags
      } catch (e) {
        console.error(e)
      }
    },
    async modifyTags() {
      try {
        const res = await Comms.api.getContactTagList({
          id: this.contactId,
          tag: this.newTag,
          modifier: this.modifier,
        })
        console.log(res)
        // this.tags = res.results
      } catch (e) {
        console.error(e)
      }
    },
    clearSearchText() {
      this.searchContactsText = ''
    },
    clearUsersText() {
      this.searchUsersText = ''
    },
    selectUser(user) {
      this.selectedUser = user
      this.toggleUserDropdown()
    },
    selectAllUsers() {
      this.selectedUser = null
      this.toggleUserDropdown()
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.contacts {
  padding: 40px;
  font-family: $thin-font-family;
  color: $dark-black-blue;

  header {
    padding: 24px 0;
  }
}

.cards-container {
  padding-top: 16px;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 24px;
}

.contact-card {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  padding: 0 16px;
  width: 25vw;
  background-color: white;
  transition: all 0.5s;
  // height: 200px;
  header {
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    justify-content: space-between;
    padding: 20px 0 8px 0;
    width: 100%;

    .main-img {
      //   margin-right: 16px;
      height: 50px;
      width: 50px;
      //   margin-bottom: 16px;
      object-fit: cover;
      cursor: text;
      border-radius: 8px;
      border: 1px solid rgba(0, 0, 0, 0.1);
    }

    div {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      justify-content: flex-start;
      gap: 8px;

      img {
        margin-right: 4px;
      }

      p {
        margin: 0;
        font-weight: bold;
      }
    }

    section {
      font-size: 14px;
    }
  }

  .body {
    line-height: 1.5;
    height: 100px;
    position: relative;
    overflow: hidden;

    p {
      margin: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      font-size: 14px;
    }
  }

  .body::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 40px;
    background: linear-gradient(to top, rgba(9, 9, 9, 0.076), rgba(255, 255, 255, 0));
    filter: blur(2px);
  }

  .footer {
    padding: 16px 0;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-end;

    p {
      margin: 0;
    }
  }

  &:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transform: scale(1.02);
  }
}

h3 {
  padding: 0;
  margin: 0;
  font-family: $base-font-family;
  font-weight: 400;
}

.more {
  display: flex;
  flex-direction: row;
  align-items: center;
  position: absolute;
  bottom: 2px;
  right: 8px;
  background-color: white;
  z-index: 3;
  font-size: 13px;
  cursor: pointer;

  padding: 2px 2px 2px 6px;
  border-bottom: 1px solid $dark-black-blue;

  img {
    filter: invert(30%);
    margin-left: 4px;
  }

  &:hover {
  }
}

.top-row {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: flex-start;

  aside {
    width: 19vw;
    padding: 0;

    img {
      margin-right: 8px;
      filter: invert(30%);
    }
  }

  section {
    width: 100%;
  }
}

.top-padding {
  padding-top: 24px;
}

.checkbox-list {
  //   max-width: 300px;
  margin: 0 auto;
  padding: 8px 0 20px 0;
  //   border: 1px solid #e0e0e0;
  //   border-radius: 8px;
  //   background-color: #fff;
}

.checkbox-list ul {
  list-style: none !important;
  padding: 0;
  margin-left: -2px;
  margin: 0;
}

.checkbox-list li {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.checkbox-list label {
  display: flex;
  align-items: center;
  width: 100%;
  font-size: 14px;
  color: #333;
}

.checkbox-list input[type='checkbox'] {
  margin-right: 10px;
}

.checkbox-list li:not(:last-child) {
  //   border-bottom: 1px solid #f0f0f0;
}

h2 {
  margin: 0;
}

.wrapper {
  display: flex;
  align-items: center;
  font-family: $thin-font-family;
  font-size: 14px;
  position: relative;
  text-align: center;
  -webkit-transform: translateZ(0); /* webkit flicker fix */
  -webkit-font-smoothing: antialiased; /* webkit text rendering fix */
}

.wrapper .tooltip {
  z-index: 10000;
  background: $dark-black-blue;
  border-radius: 4px;
  bottom: 100%;
  color: #fff;
  display: block;
  left: -34px;
  margin-bottom: 15px;
  opacity: 0;
  padding: 8px;
  pointer-events: none;
  position: absolute;
  width: 100px;
  -webkit-transform: translateY(10px);
  -moz-transform: translateY(10px);
  -ms-transform: translateY(10px);
  -o-transform: translateY(10px);
  transform: translateY(10px);
  -webkit-transition: all 0.25s ease-out;
  -moz-transition: all 0.25s ease-out;
  -ms-transition: all 0.25s ease-out;
  -o-transition: all 0.25s ease-out;
  transition: all 0.25s ease-out;
  -webkit-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -moz-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -ms-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -o-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
}

.wrapper .tooltip:before {
  bottom: -20px;
  content: ' ';
  display: block;
  height: 20px;
  left: 0;
  position: absolute;
  width: 100%;
}

.wrapper .tooltip:after {
  border-left: solid transparent 10px;
  border-right: solid transparent 10px;
  border-top: solid $dark-black-blue 10px;
  bottom: -10px;
  content: ' ';
  height: 0;
  left: 50%;
  margin-left: -13px;
  position: absolute;
  width: 0;
}

.wrapper:hover .tooltip {
  opacity: 1;
  pointer-events: auto;
  -webkit-transform: translateY(0px);
  -moz-transform: translateY(0px);
  -ms-transform: translateY(0px);
  -o-transform: translateY(0px);
  transform: translateY(0px);
}

.lte8 .wrapper .tooltip {
  display: none;
}

.lte8 .wrapper:hover .tooltip {
  display: block;
}

.space-between {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

::placeholder {
  color: rgba(0, 0, 0, 0.4);
}

.input {
  position: sticky;
  z-index: 8;
  top: 1.5rem;
  width: 25vw;
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-family: $thin-font-family;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 11px 20px 11px 10px;
}

.search-input {
  border: none;
  outline: none;
  margin-left: 0.5rem;
  width: 100%;
}

.pointer {
  cursor: pointer;
}

.relative {
  position: relative;
}
.dropdown {
  position: absolute;
  top: 40px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 8px;
  left: 16px;
  z-index: 6;
  min-width: 25vw;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);

  .dropdown-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 8px;

    img {
      margin-right: 8px;
    }
  }

  .dropdown-body {
    padding: 0 8px;
    max-height: 250px;
    overflow: scroll;
  }

  .dropdown-item {
    padding: 8px 0;
    cursor: pointer;
    width: 100%;
  }

  .dropdown-item:last-of-type {
    border-bottom: none;
  }

  .dropdown-item:hover {
    opacity: 0.7;
  }

  .dropdown-footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding: 24px 8px 12px 8px;
  }
}

.col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;

  p {
    font-family: $base-font-family;
  }
}
.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.primary-button {
  @include dark-blue-button();
  border: none;
  border-radius: 16px;

  img {
    filter: invert(100%);
    margin-right: 4px;
  }
}

.secondary-button {
  @include dark-blue-button();
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: $dark-black-blue;
  border-radius: 16px;

  img {
    filter: invert(30%);
  }
}
</style>
