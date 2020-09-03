var vm = new Vue({
  el: '#app',
  data: {
    api_url : 'http://ip:端口/reply/api/',
    tableData : [],
    dialogFormVisible : false,
    form: {
      word: '',
      reply: ''
    },
    formLabelWidth: '120px',
    trigger : "fullmatch",
    fileList : [],
    cqcode : '',
    copyDisable : false,
    varDialogVisible : false,
    varData : [{
      var : '【艾特全体】',
      desc : '艾特全体成员'
    },{
      var : '【艾特当前】',
      desc : '艾特触发本回复的成员'
    },{
      var : '【随机图片<文件夹>】',
      desc : '随机发送文件夹内一张图片'
    },{
      var : '【随机语音<文件夹>】',
      desc : '随机发送文件夹内一条语音'
    }]
  },
  
  mounted() {
    this.refresh();
  },

  methods: {
    refresh: function (){
      var thisvue = this;
      axios.get(thisvue.api_url + 'show'
      ).then(function (resp) {
        thisvue.tableData = resp.data.data;
      }).catch(function (error) {
        thisvue.$alert(error, '加载数据错误')
      });
    },

    delete_rec: function(scope){
      var thisvue = this;
      var row = scope.$index;
      thisvue.$confirm('是否删除 "' + scope.row.word + '"', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'danger'
      }).then(() => {
        thisvue.tableData.splice(row, 1);
        axios.post(thisvue.api_url + 'delete', {
          "word" : scope.row.word,
          "trigger" : scope.row.trigger
        }).catch(function(error) {
          thisvue.$message.error('删除失败')
        })
      })
    },

    add_rec: function(){
      var thisvue = this;
      if (thisvue.form.word == '' || thisvue.form.reply == ''){
        thisvue.$message.error('触发词或者回复为空，添加失败');
        return;
      }
      var rec = {
        "trigger" : thisvue.trigger,
        "word" : thisvue.form.word,
        "reply" : thisvue.form.reply
      }
      thisvue.dialogFormVisible = false;
      axios.post(thisvue.api_url + 'add', rec).then(function(resp){
        if(resp.data == 'success'){
          thisvue.$message.info('添加成功')
          thisvue.form.word = ''
          thisvue.form.reply = ''
        }
      }).catch(function(error){
        thisvue.$message.error('添加失败')
      })
    },

    handleRemove: function(file, fileList) {
      console.log(file, fileList);
    },
    handlePreview: function(file) {
      console.log(file);
    },
    handleExceed: function(files, fileList) {
      this.$message.warning(`当前限制选择 1 个文件，本次选择了 ${files.length} 个文件，共选择了 ${files.length + fileList.length} 个文件`);
    },
    beforeRemove: function(file, fileList) {
      return this.$confirm(`确定移除 ${ file.name }？`);
    },
    uploadSuccess: function(resp, file, fileList){
      var thisvue = this;
      thisvue.cqcode = resp
    },

    uploadError: function(resp, file, fileList){
      this.$alert('上传失败，请检查文件类型')
    },

    doCopy: function(){
      this.$copyText(this.cqcode).then(function (e){
        this.$alert('已复制')
      });
    },

    copyVar: function(scope){
      var thisvue = this;
      thisvue.$copyText(scope.row.var).then(function (e){
        thisvue.$alert('已复制')
      });
    }

  },

  delimiters: ['[[', ']]'],
})
