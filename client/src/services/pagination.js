const PaginationDefaults = {
  page: 1,
  totalCount: null,
  next: null,
  previous: null,
  size: 25,
}

const Pagination = {
  create(opts = {}) {
    return Object.assign(Object.create(Pagination), PaginationDefaults, { ...opts })
  },
  calcTotalPages(pagination) {
    const { totalCount, size } = pagination
    if (!totalCount) {
      return null
    }
    return Math.ceil(totalCount / size)
  },
  setNextPage() {
    if (this.page === this.calcTotalPages) return
    this.page++
  },
  setPrevPage() {
    if (this.page === 1) return
    this.page--
  },
  get hasPrevPage() {
    return this.page > 1
  },
  get hasNextPage() {
    return this.calcTotalPages(this) && this.page !== this.calcTotalPages(this)
  },
  get currentPageStart() {
    return this.page > 1 ? (this.page - 1) * this.size : 1
  },
  get currentPageEnd() {
    return Math.min(this.page > 1 ? this.page * this.size : this.size, this.totalCount)
  },
}

export const paginationMixin = {
  data() {
    return {
      // this is added in case collection.refreshing cannot be used for conditional render,
      // such as if it is used somewhere else in UX.
      pagination: {
        loading: false,
      },
    }
  },
  methods: {
    startPaginationLoading(ref) {
      // if the ref is not visible in viewport, scroll viewport to it.
      let top = ref.offsetTop
      let bounding = ref.getBoundingClientRect()
      let refVisible =
        bounding.top >= 0 &&
        bounding.bottom <= (window.innerHeight || document.documentElement.clientHeight)

      if (!refVisible) {
        window.scrollTo(0, top)
      }
      this.pagination.loading = true
    },
  },
}

export default Pagination
