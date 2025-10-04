#!/usr/bin/env ruby
# frozen_string_literal: true

=begin
▛//▞▞ ⟦⎊⟧ :: CLOUD.STRATOS :: ORCHESTRATION.LAYER ⫸

Ruby-based orchestration layer for:
- Templating op specs
- Rapid iteration on ritual structures
- Memory coordination between layers
- Temporary data management

This is the "cloud" layer - holds ephemeral state and
coordinates between engine.stratos (Rust) and r-layer.
=end

require 'erb'
require 'json'
require 'yaml'
require 'fileutils'
require 'digest'

module CloudStratos
  VERSION = '1.0.0'
  
  # Ritual markers
  class Ritual
    attr_accessor :ask, :boot, :seal, :auth_key
    
    def initialize(ask: '///▙', boot: '⟦⎊⟧', seal: '::∎', auth_key: nil)
      @ask = ask
      @boot = boot
      @seal = seal
      @auth_key = auth_key
    end
    
    # Compute auth hash (matches Rust implementation)
    def compute_auth(secret)
      payload = "#{@ask}#{@boot}#{@seal}#{secret}"
      Digest::SHA256.hexdigest(payload)
    end
    
    # Sign this ritual with secret
    def sign!(secret)
      @auth_key = compute_auth(secret)
      self
    end
    
    # Validate auth
    def valid?(secret)
      return true if @auth_key.nil? # unsigned rituals allowed
      @auth_key == compute_auth(secret)
    end
  end
  
  # Memory store for inter-layer communication
  class Memory
    def initialize(base_dir: 'work/memory')
      @base_dir = base_dir
      FileUtils.mkdir_p(@base_dir)
    end
    
    def store(key, value, ttl: nil)
      data = {
        value: value,
        stored_at: Time.now.to_i,
        ttl: ttl
      }
      File.write(path_for(key), JSON.pretty_generate(data))
    end
    
    def recall(key)
      path = path_for(key)
      return nil unless File.exist?(path)
      
      data = JSON.parse(File.read(path))
      
      # Check TTL
      if data['ttl']
        age = Time.now.to_i - data['stored_at']
        return nil if age > data['ttl']
      end
      
      data['value']
    end
    
    def exists?(key)
      File.exist?(path_for(key))
    end
    
    def delete(key)
      File.delete(path_for(key)) if exists?(key)
    end
    
    def list
      Dir.glob("#{@base_dir}/*.json").map do |f|
        File.basename(f, '.json')
      end
    end
    
    private
    
    def path_for(key)
      safe_key = key.gsub(/[^a-zA-Z0-9_-]/, '_')
      "#{@base_dir}/#{safe_key}.json"
    end
  end
  
  # Template renderer for op specs
  class SpecBuilder
    def initialize(template_path: nil)
      @template_path = template_path
      @vars = {}
      @ritual = Ritual.new
      @meta = {}
      @kernel = default_kernel
      @plan = []
    end
    
    def ritual(ask: nil, boot: nil, seal: nil)
      @ritual.ask = ask if ask
      @ritual.boot = boot if boot
      @ritual.seal = seal if seal
      self
    end
    
    def meta(name:, version:, operator:, tags: [])
      @meta = { name: name, version: version, operator: operator, tags: tags }
      self
    end
    
    def kernel(purpose: nil, rules: nil, identity: nil, structure: nil, motion: nil)
      @kernel[:purpose] = purpose if purpose
      @kernel[:rules] = rules if rules
      @kernel[:identity] = identity if identity
      @kernel[:structure] = structure if structure
      @kernel[:motion] = motion if motion
      self
    end
    
    def add_step(step)
      @plan << step
      self
    end
    
    def shell(id:, cmd:, cwd: nil)
      add_step({ type: 'shell', id: id, cmd: cmd, cwd: cwd }.compact)
    end
    
    def llm(id:, prompt:, model: nil, max_tokens: nil)
      add_step({ type: 'llm', id: id, prompt: prompt, model: model, max_tokens: max_tokens }.compact)
    end
    
    def ruby(id:, script:, args: [])
      add_step({ type: 'ruby', id: id, script: script, args: args })
    end
    
    def r(id:, script:, output: nil)
      add_step({ type: 'r', id: id, script: script, output: output }.compact)
    end
    
    def validate(id:, check:, on_fail: nil)
      add_step({ type: 'validate', id: id, check: check, on_fail: on_fail }.compact)
    end
    
    def store(id:, key:, value:)
      add_step({ type: 'store', id: id, key: key, value: value })
    end
    
    def recall(id:, key:)
      add_step({ type: 'recall', id: id, key: key })
    end
    
    def sign(secret)
      @ritual.sign!(secret)
      self
    end
    
    def build
      spec = {
        ritual: {
          ask: @ritual.ask,
          boot: @ritual.boot,
          seal: @ritual.seal
        },
        meta: @meta,
        kernel: @kernel,
        plan: @plan
      }
      
      # Add auth_key if signed
      spec[:ritual][:auth_key] = @ritual.auth_key if @ritual.auth_key
      
      spec
    end
    
    def to_toml
      require 'toml-rb' rescue require 'tomlrb'
      TomlRB.dump(build)
    end
    
    def save(path)
      File.write(path, to_toml)
      puts "✓ Saved op spec: #{path}"
      path
    end
    
    private
    
    def default_kernel
      {
        purpose: ['define.actions', 'map.tasks', 'establish.goal'],
        rules: ['enforce.laws', 'prevent.drift', 'validate.steps'],
        identity: ['sources', 'roles', 'context', 'trace'],
        structure: ['step', 'check', 'persist', 'advance'],
        motion: ['artifacts', 'reports', 'states']
      }
    end
  end
  
  # Executor that calls engine.stratos
  class Executor
    def initialize(engine_path: '../engine/target/release/stratos', secret: nil)
      @engine_path = engine_path
      @secret = secret || ENV['CODEX_SECRET'] || 'default-secret'
    end
    
    def execute(spec_path)
      puts "▛//▞▞ ⟦⎊⟧ :: CLOUD.STRATOS :: EXECUTING ⫸"
      puts "  Spec: #{spec_path}"
      puts "  Engine: #{@engine_path}"
      
      # Set secret in environment
      env = { 'CODEX_SECRET' => @secret }
      
      # Call engine.stratos
      output = `CODEX_SECRET=#{@secret} #{@engine_path} #{spec_path} 2>&1`
      status = $?.exitstatus
      
      if status == 0
        puts "\n✓ Execution successful"
      else
        puts "\n✗ Execution failed (exit: #{status})"
      end
      
      puts output
      status == 0
    end
  end
end

# CLI interface when run directly
if __FILE__ == $PROGRAM_NAME
  require 'optparse'
  
  options = {}
  OptionParser.new do |opts|
    opts.banner = "Usage: cloud.stratos.rb [command] [options]"
    
    opts.on('-s', '--spec PATH', 'Op spec path') { |v| options[:spec] = v }
    opts.on('-o', '--output PATH', 'Output path') { |v| options[:output] = v }
    opts.on('-k', '--key KEY', 'Memory key') { |v| options[:key] = v }
    opts.on('-v', '--value VALUE', 'Memory value') { |v| options[:value] = v }
  end.parse!
  
  command = ARGV.shift
  
  case command
  when 'execute'
    executor = CloudStratos::Executor.new
    spec_path = options[:spec] || 'codex.op.toml'
    executor.execute(spec_path)
    
  when 'store'
    memory = CloudStratos::Memory.new
    memory.store(options[:key], options[:value])
    puts "✓ Stored: #{options[:key]}"
    
  when 'recall'
    memory = CloudStratos::Memory.new
    value = memory.recall(options[:key])
    if value
      puts value.is_a?(String) ? value : JSON.pretty_generate(value)
    else
      puts "Key not found: #{options[:key]}"
      exit 1
    end
    
  when 'list'
    memory = CloudStratos::Memory.new
    keys = memory.list
    puts "Memory keys (#{keys.size}):"
    keys.each { |k| puts "  • #{k}" }
    
  else
    puts "Commands: execute, store, recall, list"
    exit 1
  end
end
